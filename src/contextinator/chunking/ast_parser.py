"""
Abstract Syntax Tree (AST) parsing module for Contextinator.

This module provides functionality to parse source code files using Tree-sitter
parsers and extract semantic code chunks like functions, classes, and methods.
"""

from pathlib import Path
import uuid
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..config import SUPPORTED_EXTENSIONS
from ..utils.logger import logger

# Tree-sitter imports with graceful fallback
try:
    from tree_sitter import Language, Parser
    
    # Language-specific imports
    import tree_sitter_bash
    import tree_sitter_c
    import tree_sitter_c_sharp
    import tree_sitter_cpp
    import tree_sitter_go
    import tree_sitter_java
    import tree_sitter_javascript
    import tree_sitter_json
    import tree_sitter_kotlin
    import tree_sitter_lua
    import tree_sitter_markdown
    import tree_sitter_php
    import tree_sitter_python
    import tree_sitter_rust
    import tree_sitter_solidity
    import tree_sitter_sql
    import tree_sitter_swift
    import tree_sitter_toml
    import tree_sitter_typescript
    import tree_sitter_yaml
    
    # Optional: dockerfile (not available on Windows)
    try:
        import tree_sitter_dockerfile
        HAS_DOCKERFILE = True
    except ImportError:
        tree_sitter_dockerfile = None
        HAS_DOCKERFILE = False
        logger.debug("tree-sitter-dockerfile not available (Windows platform)")
    
    # Optional: HTML parser
    try:
        import tree_sitter_html
        HAS_HTML = True
    except ImportError:
        tree_sitter_html = None
        HAS_HTML = False
        logger.debug("tree-sitter-html not available")
    
    # Optional: CSS parser
    try:
        import tree_sitter_css
        HAS_CSS = True
    except ImportError:
        tree_sitter_css = None
        HAS_CSS = False
        logger.debug("tree-sitter-css not available")
    
    # Optional: Additional language parsers
    try:
        import tree_sitter_zig
        HAS_ZIG = True
    except ImportError:
        tree_sitter_zig = None
        HAS_ZIG = False
    
    try:
        import tree_sitter_ruby
        HAS_RUBY = True
    except ImportError:
        tree_sitter_ruby = None
        HAS_RUBY = False
    
    try:
        import tree_sitter_scala
        HAS_SCALA = True
    except ImportError:
        tree_sitter_scala = None
        HAS_SCALA = False
    
    try:
        import tree_sitter_haskell
        HAS_HASKELL = True
    except ImportError:
        tree_sitter_haskell = None
        HAS_HASKELL = False
    
    try:
        import tree_sitter_ocaml
        HAS_OCAML = True
    except ImportError:
        tree_sitter_ocaml = None
        HAS_OCAML = False
    
    try:
        import tree_sitter_elixir
        HAS_ELIXIR = True
    except ImportError:
        tree_sitter_elixir = None
        HAS_ELIXIR = False
    
    try:
        import tree_sitter_hcl
        HAS_HCL = True
    except ImportError:
        tree_sitter_hcl = None
        HAS_HCL = False
    
    try:
        import tree_sitter_make
        HAS_MAKE = True
    except ImportError:
        tree_sitter_make = None
        HAS_MAKE = False
    
    try:
        import tree_sitter_xml
        HAS_XML = True
    except ImportError:
        tree_sitter_xml = None
        HAS_XML = False
    
    from .ast_visualizer import save_ast_visualization
    
    # Language module mapping for parser creation
    LANGUAGE_MODULES: Dict[str, Any] = {
        'python': tree_sitter_python,
        'javascript': tree_sitter_javascript, 
        'typescript': tree_sitter_typescript,
        'tsx': tree_sitter_typescript,  # TSX uses the same TypeScript module
        'java': tree_sitter_java,
        'go': tree_sitter_go,
        'rust': tree_sitter_rust,
        'cpp': tree_sitter_cpp,
        'c': tree_sitter_c,
        'csharp': tree_sitter_c_sharp,
        'cs': tree_sitter_c_sharp,  # Alternative C# extension
        'php': tree_sitter_php,
        'bash': tree_sitter_bash,
        'sh': tree_sitter_bash,  # Shell scripts
        'sql': tree_sitter_sql,
        'kotlin': tree_sitter_kotlin,
        'kt': tree_sitter_kotlin,  # Kotlin extension
        'yaml': tree_sitter_yaml,
        'yml': tree_sitter_yaml,  # Alternative YAML extension
        'markdown': tree_sitter_markdown,
        'md': tree_sitter_markdown,  # Markdown extension
        'json': tree_sitter_json,
        'toml': tree_sitter_toml,
        'swift': tree_sitter_swift,
        'solidity': tree_sitter_solidity,
        'sol': tree_sitter_solidity,  # Solidity extension
        'lua': tree_sitter_lua,
    }
    
    # Add dockerfile support if available (platform-dependent)
    if HAS_DOCKERFILE:
        LANGUAGE_MODULES['dockerfile'] = tree_sitter_dockerfile
    if HAS_HTML:
        LANGUAGE_MODULES['html'] = tree_sitter_html
        LANGUAGE_MODULES['htm'] = tree_sitter_html
    if HAS_CSS:
        LANGUAGE_MODULES['css'] = tree_sitter_css
        LANGUAGE_MODULES['scss'] = tree_sitter_css
        LANGUAGE_MODULES['sass'] = tree_sitter_css
        LANGUAGE_MODULES['less'] = tree_sitter_css
    if HAS_ZIG:
        LANGUAGE_MODULES['zig'] = tree_sitter_zig
    if HAS_RUBY:
        LANGUAGE_MODULES['ruby'] = tree_sitter_ruby
    if HAS_SCALA:
        LANGUAGE_MODULES['scala'] = tree_sitter_scala
        LANGUAGE_MODULES['sc'] = tree_sitter_scala
    if HAS_HASKELL:
        LANGUAGE_MODULES['haskell'] = tree_sitter_haskell
        LANGUAGE_MODULES['lhs'] = tree_sitter_haskell
    if HAS_OCAML:
        LANGUAGE_MODULES['ocaml'] = tree_sitter_ocaml
        LANGUAGE_MODULES['mli'] = tree_sitter_ocaml
    if HAS_ELIXIR:
        LANGUAGE_MODULES['elixir'] = tree_sitter_elixir
        LANGUAGE_MODULES['ex'] = tree_sitter_elixir
        LANGUAGE_MODULES['exs'] = tree_sitter_elixir
    if HAS_HCL:
        LANGUAGE_MODULES['hcl'] = tree_sitter_hcl
        LANGUAGE_MODULES['tf'] = tree_sitter_hcl
        LANGUAGE_MODULES['tfvars'] = tree_sitter_hcl
    if HAS_MAKE:
        LANGUAGE_MODULES['make'] = tree_sitter_make
    if HAS_XML:
        LANGUAGE_MODULES['xml'] = tree_sitter_xml
    
    TREE_SITTER_AVAILABLE = True
    logger.info("Tree-sitter imports successful")
    
except ImportError as e:
    TREE_SITTER_AVAILABLE = False
    LANGUAGE_MODULES = {}
    logger.warning(f"Tree-sitter import failed: {e}")
    logger.info("💡 Install missing modules with: pip install tree-sitter tree-sitter-python tree-sitter-javascript ...")
    
    if TYPE_CHECKING:
        from tree_sitter import Parser

# Node types to extract per language for semantic chunking
NODE_TYPES: Dict[str, List[str]] = {
    'python': ['function_definition', 'class_definition', 'decorated_definition', 'import_statement', 'import_from_statement'],
    'javascript': ['function_declaration', 'function_expression', 'arrow_function', 'class_declaration', 'method_definition', 'import_statement'],
    'typescript': ['function_declaration', 'function_expression', 'arrow_function', 'class_declaration', 'method_definition', 'interface_declaration', 'import_statement', 'lexical_declaration', 'expression_statement', 'export_statement'],
     'tsx': ['function_declaration', 'function_expression', 'arrow_function', 'class_declaration', 'method_definition', 'interface_declaration', 'import_statement', 'lexical_declaration', 'expression_statement', 'export_statement'],
    'java': ['class_declaration', 'method_declaration', 'constructor_declaration', 'interface_declaration', 'import_declaration'],
    'go': ['function_declaration', 'method_declaration', 'type_declaration', 'import_declaration'],
    'rust': ['function_item', 'impl_item', 'struct_item', 'enum_item', 'trait_item', 'use_declaration'],
    'cpp': ['function_definition', 'class_specifier', 'struct_specifier', 'preproc_include'],
    'c': ['function_definition', 'struct_specifier', 'preproc_include'],
    'csharp': ['class_declaration', 'method_declaration', 'constructor_declaration', 'interface_declaration', 'property_declaration', 'using_directive'],
    'cs': ['class_declaration', 'method_declaration', 'constructor_declaration', 'interface_declaration', 'property_declaration', 'using_directive'],
    'php': ['function_definition', 'class_declaration', 'method_declaration', 'namespace_use_declaration'],
    'bash': ['function_definition', 'command'],
    'sh': ['function_definition', 'command'],
    'sql': ['statement', 'create_table', 'create_index', 'select', 'insert', 'update', 'delete'],
    'kotlin': ['class_declaration', 'function_declaration', 'property_declaration', 'object_declaration', 'import_header'],
    'kt': ['class_declaration', 'function_declaration', 'property_declaration', 'object_declaration', 'import_header'],
    'yaml': ['block_mapping', 'block_sequence'],
    'yml': ['block_mapping', 'block_sequence'],
    'markdown': ['section', 'heading', 'code_block'],
    'md': ['section', 'heading', 'code_block'],
    'dockerfile': ['instruction'],
    'json': ['object', 'array'],
    'toml': ['table', 'key_value'],
    'swift': ['class_declaration', 'function_declaration', 'protocol_declaration', 'struct_declaration', 'import_declaration'],
    'solidity': ['contract_declaration', 'function_definition', 'struct_definition', 'event_definition'],
    'sol': ['contract_declaration', 'function_definition', 'struct_definition', 'event_definition'],
    'lua': ['function_definition', 'local_function', 'table_constructor'],
    'html': ['element', 'script_element', 'style_element'],
    'htm': ['element', 'script_element', 'style_element'],
    'css': ['rule_set', 'media_statement', 'keyframes_statement'],
    'scss': ['rule_set', 'media_statement', 'keyframes_statement'],
    'sass': ['rule_set', 'media_statement', 'keyframes_statement'],
    'less': ['rule_set', 'media_statement', 'keyframes_statement'],
    'zig': ['function_declaration', 'struct_declaration', 'enum_declaration'],
    'ruby': ['method', 'class', 'module', 'def'],
    'scala': ['class_definition', 'object_definition', 'trait_definition', 'function_definition'],
    'sc': ['class_definition', 'object_definition', 'trait_definition', 'function_definition'],
    'haskell': ['function_declaration', 'type_declaration', 'data_declaration'],
    'lhs': ['function_declaration', 'type_declaration', 'data_declaration'],
    'ocaml': ['value_definition', 'type_definition', 'module_definition'],
    'mli': ['value_specification', 'type_definition', 'module_specification'],
    'elixir': ['call', 'def', 'defmodule', 'defp'],
    'ex': ['call', 'def', 'defmodule', 'defp'],
    'exs': ['call', 'def', 'defmodule', 'defp'],
    'hcl': ['block', 'attribute'],
    'tf': ['block', 'attribute'],
    'tfvars': ['attribute'],
    'make': ['rule', 'variable_assignment'],
    'xml': ['element', 'STag'],
    'prisma': ['model', 'generator', 'datasource', 'enum']
}


PARENT_NODE_TYPES: Dict[str, List[str]] = {
    'python': ['class_definition'],
    'javascript': ['class_declaration'],
    'typescript': ['class_declaration', 'interface_declaration'],
    'tsx': ['class_declaration', 'interface_declaration'],
    'java': ['class_declaration', 'interface_declaration'],
    'go': ['type_declaration'],
    'rust': ['impl_item', 'struct_item', 'enum_item', 'trait_item'],
    'cpp': ['class_specifier', 'struct_specifier'],
    'c': ['struct_specifier'],
    'csharp': ['class_declaration', 'interface_declaration'],
    'cs': ['class_declaration', 'interface_declaration'],
    'php': ['class_declaration'],
    'bash': [],
    'sh': [],
    'sql': [],
    'kotlin': ['class_declaration', 'object_declaration'],
    'kt': ['class_declaration', 'object_declaration'],
    'yaml': [],
    'yml': [],
    'markdown': [],
    'md': [],
    'dockerfile': [],
    'json': [],
    'toml': [],
    'swift': ['class_declaration', 'struct_declaration', 'protocol_declaration'],
    'solidity': ['contract_declaration', 'struct_definition'],
    'sol': ['contract_declaration', 'struct_definition'],
    'lua': ['table_constructor'],
    'html': [],
    'htm': [],
    'css': [],
    'scss': [],
    'sass': [],
    'less': [],
    'zig': ['struct_declaration', 'enum_declaration'],
    'ruby': ['class', 'module'],
    'scala': ['class_definition', 'object_definition', 'trait_definition'],
    'sc': ['class_definition', 'object_definition', 'trait_definition'],
    'haskell': [],
    'lhs': [],
    'ocaml': ['module_definition'],
    'mli': ['module_specification'],
    'elixir': ['defmodule'],
    'ex': ['defmodule'],
    'exs': ['defmodule'],
    'prisma': ['model'],
    'hcl': [],
    'tf': [],
    'tfvars': [],
    'make': [],
    'xml': [],
}

# Cache for parsers to avoid recreation
_parser_cache: Dict[str, "Parser"] = {}
# Lock for thread-safe parser cache access
import threading
_parser_cache_lock = threading.Lock()


def parse_file(
    file_path: Path, 
    save_ast: bool = False, 
    chunks_dir: Optional[Path] = None,
    repo_path: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """
    Parse a file and return its AST representation with extracted nodes.
    
    Args:
        file_path: Path to the file to parse (absolute path)
        save_ast: Whether to save AST visualization data
        chunks_dir: Repository-specific chunks directory for AST data (required if save_ast=True)
        repo_path: Repository root path for computing relative paths (optional)
    
    Returns:
        Dictionary containing AST nodes and metadata, or None if parsing fails
        
    Raises:
        ValidationError: If save_ast is True but chunks_dir is None
        FileSystemError: If file cannot be read
    """
    from ..utils.exceptions import ValidationError, FileSystemError, ParsingError
    
    if save_ast and chunks_dir is None:
        raise ValidationError("chunks_dir is required when save_ast=True", "chunks_dir", "Path object")
    
    # Compute repo-relative path with forward slashes for cross-platform compatibility
    if repo_path:
        try:
            relative_path = file_path.relative_to(repo_path)
            # Convert to forward slashes for consistency
            file_path_str = relative_path.as_posix()
        except ValueError:
            # If file is not relative to repo_path, use absolute path
            logger.warning(f"File {file_path} is not within repo {repo_path}, using absolute path")
            file_path_str = str(file_path)
    else:
        file_path_str = str(file_path)
        
    try:
        language = SUPPORTED_EXTENSIONS.get(file_path.suffix)
        if not language:
            logger.debug(f"Unsupported file extension: {file_path.suffix}")
            return None
        
        # Special handling for Jupyter Notebook files
        if language == 'ipynb':
            from .notebook_parser import parse_notebook
            return parse_notebook(file_path, repo_path=repo_path)
        
        # Handle file reading errors gracefully
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except (OSError, IOError, PermissionError) as e:
            raise FileSystemError(f"Cannot read file: {e}", str(file_path), "read")
        
        if not TREE_SITTER_AVAILABLE:
            # Fallback when Tree-sitter unavailable
            logger.warning(f"Tree-sitter not available, using fallback for {file_path}")
            result = _fallback_parse(file_path, file_path_str, language, content)
            
            if save_ast and chunks_dir:
                _save_ast_safely(file_path, language, None, content, result['nodes'], chunks_dir, result.get('tree_info'))
            
            return result

        # Try AST parsing with fallback
        try:
            parser = get_parser(language)
            if not parser:
                logger.warning(f"No parser available for {language}, using fallback for {file_path}")
                return _fallback_parse(file_path, file_path_str, language, content)
            
            tree = parser.parse(bytes(content, 'utf-8'))
            nodes = extract_nodes(tree.root_node, content, language)
            
            logger.debug(f"Parsed {file_path} - Found {len(nodes)} semantic nodes")
            
        except Exception as e:
            # Fallback to file-level chunking on any parsing error
            logger.warning(f"AST parsing failed for {file_path}, using fallback: {e}")
            return _fallback_parse(file_path, file_path_str, language, content)
        
        # If no nodes extracted, fallback to file-level
        if not nodes:
            logger.warning(f"No semantic nodes found in {file_path}, using file-level chunking")
            result = _fallback_parse(file_path, file_path_str, language, content)
        else:
            result = {
                'file_path': file_path_str,
                'language': language,
                'content': content,
                'nodes': nodes,
                'tree_info': {
                    'has_ast': True,
                    'root_node_type': tree.root_node.type,
                    'total_nodes': _count_nodes(tree.root_node),
                    'tree_depth': _get_tree_depth(tree.root_node)
                }
            }
        
        # Save AST visualization if requested
        if save_ast and chunks_dir:
            root_node = tree.root_node if 'tree_info' in result and result['tree_info'].get('has_ast', False) else None
            _save_ast_safely(file_path, language, root_node, content, result['nodes'], chunks_dir, result.get('tree_info'))
        
        return result
    
    except (ValidationError, FileSystemError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Pattern 1: Log unexpected errors and continue
        logger.error(f"Unexpected error parsing {file_path}: {e}")
        return None


def _fallback_parse(file_path: Path, file_path_str: str, language: str, content: str) -> Dict[str, Any]:
    """
    Fallback parsing when tree-sitter is unavailable or fails.
    
    Args:
        file_path: Absolute path to the file being parsed (for logging/display)
        file_path_str: Repo-relative file path string to store in metadata
        language: Programming language identifier
        content: File content
        
    Returns:
        Dictionary with file-level chunk information
    """
    return {
        'file_path': file_path_str,
        'language': language,
        'content': content,
        'nodes': [{
            'id': str(uuid.uuid4()),
            'type': 'file',
            'name': file_path.name,
            'content': content,
            'start_line': 1,
            'end_line': len(content.splitlines()),
            'start_byte': 0,
            'end_byte': len(content.encode('utf-8')),
            'parent_id': None,
            'parent_type': None,
            'parent_name': None,
            'is_parent': False,
            'children_ids': []
        }],
        'tree_info': {
            'has_ast': False,
            'fallback_reason': 'tree-sitter not available or language modules missing',
            'parser_available': TREE_SITTER_AVAILABLE
        }
    }


def get_parser(language: str) -> Optional["Parser"]:
    """
    Get tree-sitter parser for language with caching.
    
    Thread-safe parser retrieval with lazy initialization.
    
    Args:
        language: Programming language identifier
        
    Returns:
        Parser instance or None if unavailable
    """
    global _parser_cache
    
    if not TREE_SITTER_AVAILABLE:
        return None
    
    # Fast path: return cached parser without lock if available
    if language in _parser_cache:
        return _parser_cache[language]
    
    # Slow path: create parser with lock to avoid race conditions
    with _parser_cache_lock:
        # Double-check after acquiring lock (another thread might have created it)
        if language in _parser_cache:
            return _parser_cache[language]
        
        try:
            # Get language module
            lang_module = LANGUAGE_MODULES.get(language)
            if not lang_module:
                logger.warning(f"No language module available for {language}")
                return None
            
            # Handle special cases for different parser APIs
            if language == 'typescript':
                lang_obj = Language(lang_module.language_typescript())
            elif language == 'tsx':
                lang_obj = Language(lang_module.language_tsx())
            elif language == 'ocaml':
                lang_obj = Language(lang_module.language_ocaml())
            elif language == 'mli':
                lang_obj = Language(lang_module.language_ocaml_interface())
            elif language == 'xml':
                lang_obj = Language(lang_module.language_xml())
            else:
                # Create Language object from module for other languages
                lang_obj = Language(lang_module.language())
            
            # Create parser with language
            parser = Parser(lang_obj)
            _parser_cache[language] = parser
            return parser
            
        except Exception as e:
            logger.warning(f"Error creating parser for {language}: {e}")
            return None

def extract_nodes(root_node: Any, content: str, language: str) -> List[Dict[str, Any]]:
    """
    Extract relevant nodes from AST based on language-specific node types.
    
    Args:
        root_node: Root node of the AST
        content: Source code content
        language: Programming language
    
    Returns:
        List of extracted nodes with metadata including hierarchy
    """
    target_types = NODE_TYPES.get(language, [])
    if not target_types:
        return []
    
    parent_types = set(PARENT_NODE_TYPES.get(language, []))
    nodes = []
    content_bytes = content.encode('utf-8')
    
    def traverse(node: Any, parent_id: Optional[str] = None, parent_info: Optional[Dict] = None) -> None:
        """Recursively traverse AST and extract target nodes with hierarchy tracking."""
        if node.type in target_types:
            node_id = str(uuid.uuid4())
            node_content = content_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
            node_name = get_node_name(node, content_bytes)
            is_parent = node.type in parent_types
            
            node_dict = {
                'id': node_id,
                'type': node.type,
                'name': node_name,
                'content': node_content,
                'start_line': node.start_point[0] + 1,
                'end_line': node.end_point[0] + 1,
                'start_byte': node.start_byte,
                'end_byte': node.end_byte,
                'is_parent': is_parent,
                'parent_id': parent_id,
                'parent_type': parent_info.get('type') if parent_info else None,
                'parent_name': parent_info.get('name') if parent_info else None,
                'children_ids': []
            }
            
            nodes.append(node_dict)
            
            if is_parent:
                for child in node.children:
                    traverse(child, node_id, {'type': node.type, 'name': node_name})
            else:
                for child in node.children:
                    traverse(child, parent_id, parent_info)
        else:
            for child in node.children:
                traverse(child, parent_id, parent_info)
    
    traverse(root_node)
    
    # Populate children_ids
    for node in nodes:
        if node['is_parent']:
            node['children_ids'] = [n['id'] for n in nodes if n['parent_id'] == node['id']]
    
    return nodes


def get_node_name(node: Any, content_bytes: bytes) -> Optional[str]:
    """
    Extract name from a node with language-aware and node-type-aware logic.
    
    Args:
        node: AST node
        content_bytes: Source code as bytes
        
    Returns:
        Node name or generated identifier
    """
    try:
        node_type = node.type
        
        # Special handling for different node types
        if node_type in ('section', 'heading'):
            for child in node.children:
                if child.type in ('atx_heading', 'setext_heading'):
                    text = content_bytes[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                    return text.strip().lstrip('#').strip()[:50]  # First 50 chars
            first_line = content_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore').split('\n')[0]
            cleaned = first_line.strip().lstrip('#').strip()[:50]
            return cleaned if cleaned else f"section_line_{node.start_point[0] + 1}"
        
        if node_type == 'arrow_function':
            parent = node.parent
            if parent and parent.type in ('variable_declarator', 'lexical_declaration'):
                for child in parent.children:
                    if child.type == 'identifier':
                        return content_bytes[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
            return f"arrow_fn_line_{node.start_point[0] + 1}"
        
        if node_type in ('object', 'block_mapping'):
            parent = node.parent
            if parent and parent.type == 'pair':
                for child in parent.children:
                    if child.type in ('string', 'flow_node', 'identifier'):
                        key = content_bytes[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                        cleaned_key = key.strip('"\'')[:30]
                        return cleaned_key
            return f"{node_type}_line_{node.start_point[0] + 1}"
        
        if node_type in ('array', 'block_sequence'):
            parent = node.parent
            if parent and parent.type == 'pair':
                for child in parent.children:
                    if child.type in ('string', 'flow_node', 'identifier'):
                        key = content_bytes[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                        cleaned_key = key.strip('"\'')[:20]
                        return f"{cleaned_key}_array"
            return f"{node_type}_line_{node.start_point[0] + 1}"

        # Generic identifier extraction
        identifier_types = {'identifier', 'name', 'property_identifier', 'type_identifier', 'field_identifier'}
        for child in node.children:
            if child.type in identifier_types:
                return content_bytes[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
        for child in node.children:
            for grandchild in child.children:
                if grandchild.type in identifier_types:
                    return content_bytes[grandchild.start_byte:grandchild.end_byte].decode('utf-8', errors='ignore')
        
        return f"anonymous_{node_type}_line_{node.start_point[0] + 1}"
        
    except Exception:
        return f"unknown_line_{node.start_point[0] + 1}" if hasattr(node, 'start_point') else None


def _save_ast_safely(file_path: Path, language: str, root_node: Any, content: str, 
                    nodes: List[Dict[str, Any]], chunks_dir: Path, tree_info: Optional[Dict[str, Any]]) -> None:
    """
    Safely save AST visualization with error handling.
    
    Args:
        file_path: Path to source file
        language: Programming language
        root_node: AST root node (None for fallback)
        content: Source code content
        nodes: Extracted nodes
        chunks_dir: Directory for AST files
        tree_info: Tree metadata
    """
    try:
        logger.debug(f"Saving AST for {file_path}")
        save_ast_visualization(str(file_path), language, root_node, content, nodes, chunks_dir, tree_info)
    except Exception as e:
        logger.warning(f"Could not save AST for {file_path}: {e}")


def _count_nodes(node: Any) -> int:
    """
    Count total number of nodes in the AST.
    
    Args:
        node: AST node
        
    Returns:
        Total node count
    """
    return 1 + sum(_count_nodes(child) for child in node.children)


def _get_tree_depth(node: Any, current_depth: int = 0) -> int:
    """
    Get the maximum depth of the AST.
    
    Args:
        node: AST node
        current_depth: Current depth level
        
    Returns:
        Maximum tree depth
    """
    if not node.children:
        return current_depth
    return max(_get_tree_depth(child, current_depth + 1) for child in node.children)


__all__ = [
    'parse_file',
    'get_parser',
    'extract_nodes',
    'get_node_name',
    'NODE_TYPES',
    'LANGUAGE_MODULES',
    'TREE_SITTER_AVAILABLE',
]
