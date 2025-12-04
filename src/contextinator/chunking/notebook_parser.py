"""
Jupyter Notebook (.ipynb) parser module for Contextinator.

This module provides functionality to parse Jupyter Notebook files and extract
semantic code chunks from individual cells, using Tree-sitter parsers for
code and markdown cells.
"""

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.logger import logger

# Lazy import for nbformat to avoid startup delay
_nbformat = None


def _get_nbformat() -> Any:
    """Lazy load nbformat module."""
    global _nbformat
    if _nbformat is None:
        try:
            import nbformat
            _nbformat = nbformat
        except ImportError as e:
            logger.warning(f"nbformat not available: {e}")
            logger.info("💡 Install nbformat with: pip install nbformat")
            raise ImportError("nbformat is required for parsing .ipynb files") from e
    return _nbformat


def parse_notebook(
    file_path: Path,
    repo_path: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """
    Parse a Jupyter Notebook file and extract nodes from each cell.

    Uses Tree-sitter parsers to parse code cells (Python) and markdown cells,
    creating semantic chunks that can be searched and embedded.

    Args:
        file_path: Path to the .ipynb file to parse (absolute path)
        repo_path: Repository root path for computing relative paths (optional)

    Returns:
        Dictionary containing parsed notebook data with nodes, or None if parsing fails

    Raises:
        FileSystemError: If file cannot be read
    """
    from ..utils.exceptions import FileSystemError

    # Compute repo-relative path with forward slashes for cross-platform compatibility
    if repo_path:
        try:
            relative_path = file_path.relative_to(repo_path)
            file_path_str = relative_path.as_posix()
        except ValueError:
            logger.warning(
                f"File {file_path} is not within repo {repo_path}, using absolute path"
            )
            file_path_str = str(file_path)
    else:
        file_path_str = str(file_path)

    try:
        # Read the notebook file
        try:
            nbformat = _get_nbformat()
            with open(file_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
        except ImportError:
            # nbformat not available - fallback to JSON parsing
            return _fallback_notebook_parse(file_path, file_path_str)
        except (OSError, IOError, PermissionError) as e:
            raise FileSystemError(f"Cannot read notebook file: {e}", str(file_path), "read")
        except Exception as e:
            logger.warning(f"Failed to parse notebook {file_path}: {e}")
            return _fallback_notebook_parse(file_path, file_path_str)

        nodes: List[Dict[str, Any]] = []
        all_content_parts: List[str] = []

        # Process each cell in the notebook
        for cell_index, cell in enumerate(nb.cells):
            cell_type = cell.cell_type
            source = cell.source if isinstance(cell.source, str) else ''.join(cell.source)

            if not source.strip():
                continue

            all_content_parts.append(f"# Cell {cell_index + 1} ({cell_type})\n{source}")

            # Determine the language for parsing based on cell type
            if cell_type == 'code':
                # Parse code cells with Python parser (most common in Jupyter)
                cell_language = 'python'
                cell_nodes = _parse_cell_content(
                    source, cell_language, cell_index, file_path_str
                )
            elif cell_type == 'markdown':
                # Parse markdown cells
                cell_language = 'markdown'
                cell_nodes = _parse_cell_content(
                    source, cell_language, cell_index, file_path_str
                )
            else:
                # Raw cells or other types - treat as plain text
                cell_nodes = _create_raw_cell_node(
                    source, cell_type, cell_index, file_path_str
                )

            nodes.extend(cell_nodes)

        if not nodes:
            # No nodes extracted - create file-level fallback
            logger.debug(
                f"No semantic nodes found in notebook {file_path}, using file-level chunking"
            )
            return _fallback_notebook_parse(file_path, file_path_str)

        full_content = '\n\n'.join(all_content_parts)

        logger.debug(
            f"Parsed notebook {file_path} - Found {len(nodes)} nodes from {len(nb.cells)} cells"
        )

        return {
            'file_path': file_path_str,
            'language': 'ipynb',
            'content': full_content,
            'nodes': nodes,
            'tree_info': {
                'has_ast': True,
                'is_notebook': True,
                'total_cells': len(nb.cells),
                'code_cells': sum(1 for c in nb.cells if c.cell_type == 'code'),
                'markdown_cells': sum(1 for c in nb.cells if c.cell_type == 'markdown'),
                'total_nodes': len(nodes)
            }
        }

    except FileSystemError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error parsing notebook {file_path}: {e}")
        return None


def _parse_cell_content(
    source: str,
    language: str,
    cell_index: int,
    file_path_str: str
) -> List[Dict[str, Any]]:
    """
    Parse cell content using the appropriate Tree-sitter parser.

    Args:
        source: Cell source code
        language: Language for parsing ('python' or 'markdown')
        cell_index: Index of the cell in the notebook (0-based)
        file_path_str: File path string for metadata

    Returns:
        List of parsed nodes from the cell
    """
    from .ast_parser import get_parser, extract_nodes, TREE_SITTER_AVAILABLE

    if not TREE_SITTER_AVAILABLE:
        return _create_raw_cell_node(source, language, cell_index, file_path_str)

    parser = get_parser(language)
    if not parser:
        return _create_raw_cell_node(source, language, cell_index, file_path_str)

    try:
        tree = parser.parse(bytes(source, 'utf-8'))
        nodes = extract_nodes(tree.root_node, source, language)

        # If no semantic nodes found, create a cell-level node
        if not nodes:
            return _create_raw_cell_node(source, language, cell_index, file_path_str)

        # Add cell context to each node
        for node in nodes:
            node['cell_index'] = cell_index
            node['cell_type'] = 'code' if language == 'python' else language
            # Prefix name with cell context for better identification
            if node.get('name'):
                node['name'] = f"cell_{cell_index + 1}:{node['name']}"
            else:
                node['name'] = f"cell_{cell_index + 1}:{node['type']}"

        return nodes

    except Exception as e:
        logger.debug(f"Failed to parse cell {cell_index} as {language}: {e}")
        return _create_raw_cell_node(source, language, cell_index, file_path_str)


def _create_raw_cell_node(
    source: str,
    cell_type: str,
    cell_index: int,
    file_path_str: str
) -> List[Dict[str, Any]]:
    """
    Create a raw node for a cell when AST parsing is not possible.

    Args:
        source: Cell source code
        cell_type: Type of cell ('code', 'markdown', 'raw', etc.)
        cell_index: Index of the cell in the notebook (0-based)
        file_path_str: File path string for metadata

    Returns:
        List containing a single cell-level node
    """
    lines = source.splitlines()
    node_id = str(uuid.uuid4())

    return [{
        'id': node_id,
        'type': f'notebook_{cell_type}_cell',
        'name': f"cell_{cell_index + 1}",
        'content': source,
        'start_line': 1,
        'end_line': max(1, len(lines)),
        'start_byte': 0,
        'end_byte': len(source.encode('utf-8')),
        'is_parent': False,
        'parent_id': None,
        'parent_type': None,
        'parent_name': None,
        'children_ids': [],
        'cell_index': cell_index,
        'cell_type': cell_type
    }]


def _fallback_notebook_parse(file_path: Path, file_path_str: str) -> Dict[str, Any]:
    """
    Fallback parsing when nbformat is unavailable or notebook parsing fails.

    Reads the notebook as JSON and creates a single file-level chunk.

    Args:
        file_path: Absolute path to the notebook file
        file_path_str: Repo-relative file path string to store in metadata

    Returns:
        Dictionary with file-level chunk information
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        logger.warning(f"Failed to read notebook {file_path}: {e}")
        content = ""

    return {
        'file_path': file_path_str,
        'language': 'ipynb',
        'content': content,
        'nodes': [{
            'id': str(uuid.uuid4()),
            'type': 'notebook_file',
            'name': file_path.name,
            'content': content,
            'start_line': 1,
            'end_line': max(1, len(content.splitlines())),
            'start_byte': 0,
            'end_byte': len(content.encode('utf-8')),
            'is_parent': False,
            'parent_id': None,
            'parent_type': None,
            'parent_name': None,
            'children_ids': []
        }],
        'tree_info': {
            'has_ast': False,
            'is_notebook': True,
            'fallback_reason': 'nbformat not available or notebook parsing failed'
        }
    }


__all__ = [
    'parse_notebook',
]
