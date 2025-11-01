from pathlib import Path
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from ..config import SUPPORTED_EXTENSIONS
from ..utils.logger import logger

try:
    from tree_sitter import Parser, Language
    import tree_sitter_python
    import tree_sitter_javascript
    import tree_sitter_typescript
    import tree_sitter_java
    import tree_sitter_go
    import tree_sitter_rust
    import tree_sitter_cpp
    import tree_sitter_c
    import tree_sitter_c_sharp
    import tree_sitter_php
    import tree_sitter_bash
    import tree_sitter_sql
    import tree_sitter_kotlin
    import tree_sitter_yaml
    import tree_sitter_markdown
    import tree_sitter_dockerfile
    import tree_sitter_json
    import tree_sitter_toml
    import tree_sitter_swift
    import tree_sitter_solidity
    import tree_sitter_lua
    from .ast_visualizer import save_ast_visualization
    
    # Language module mapping
    LANGUAGE_MODULES = {
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
        'dockerfile': tree_sitter_dockerfile,
        'json': tree_sitter_json,
        'toml': tree_sitter_toml,
        'swift': tree_sitter_swift,
        'solidity': tree_sitter_solidity,
        'sol': tree_sitter_solidity,  # Solidity extension
        'lua': tree_sitter_lua,
    }
    
    TREE_SITTER_AVAILABLE = True
    logger.info("Tree-sitter imports successful")
except ImportError as e:
    TREE_SITTER_AVAILABLE = False
    LANGUAGE_MODULES = {}
    logger.warning(f"Tree-sitter import failed: {e}")
    logger.info("💡 Install missing modules with: pip install tree-sitter tree-sitter-python tree-sitter-javascript ...")
    if TYPE_CHECKING:
        from tree_sitter import Parser


# Node types to extract per language
NODE_TYPES = {
    'python': ['function_definition', 'class_definition', 'decorated_definition'],
    'javascript': ['function_declaration', 'function_expression', 'arrow_function', 'class_declaration', 'method_definition'],
    'typescript': ['function_declaration', 'function_expression', 'arrow_function', 'class_declaration', 'method_definition', 'interface_declaration'],
    'tsx': ['function_declaration', 'function_expression', 'arrow_function', 'class_declaration', 'method_definition', 'interface_declaration'],
    'java': ['class_declaration', 'method_declaration', 'constructor_declaration', 'interface_declaration'],
    'go': ['function_declaration', 'method_declaration', 'type_declaration'],
    'rust': ['function_item', 'impl_item', 'struct_item', 'enum_item', 'trait_item'],
    'cpp': ['function_definition', 'class_specifier', 'struct_specifier'],
    'c': ['function_definition', 'struct_specifier'],
    'csharp': ['class_declaration', 'method_declaration', 'constructor_declaration', 'interface_declaration', 'property_declaration'],
    'cs': ['class_declaration', 'method_declaration', 'constructor_declaration', 'interface_declaration', 'property_declaration'],
    'php': ['function_definition', 'class_declaration', 'method_declaration'],
    'bash': ['function_definition', 'command'],
    'sh': ['function_definition', 'command'],
    'sql': ['create_table_statement', 'create_view_statement', 'create_function_statement', 'create_procedure_statement'],
    'kotlin': ['class_declaration', 'function_declaration', 'property_declaration', 'object_declaration'],
    'kt': ['class_declaration', 'function_declaration', 'property_declaration', 'object_declaration'],
    'yaml': ['block_mapping', 'block_sequence'],
    'yml': ['block_mapping', 'block_sequence'],
    'markdown': ['section', 'heading', 'code_block'],
    'md': ['section', 'heading', 'code_block'],
    'dockerfile': ['instruction'],
    'json': ['object', 'array'],
    'toml': ['table', 'key_value'],
    'swift': ['class_declaration', 'function_declaration', 'protocol_declaration', 'struct_declaration'],
    'solidity': ['contract_declaration', 'function_definition', 'struct_definition', 'event_definition'],
    'sol': ['contract_declaration', 'function_definition', 'struct_definition', 'event_definition'],
    'lua': ['function_definition', 'local_function', 'table_constructor'],
}

# Cache for parsers
_parser_cache = {}


def parse_file(file_path: Path, save_ast: bool = False, chunks_dir: Path = None) -> Optional[Dict[str, Any]]:
    """
    Parse a file and return its AST representation with extracted nodes.
    
    Args:
        file_path: Path to the file to parse
        save_ast: Whether to save AST visualization data
        chunks_dir: Repository-specific chunks directory for AST data (required if save_ast=True)
    
    Returns:
        Dictionary containing AST nodes and metadata, or None if parsing fails
    """
    try:
        language = SUPPORTED_EXTENSIONS.get(file_path.suffix)
        if not language:
            return None
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if not TREE_SITTER_AVAILABLE:
            # Fallback: return entire file as one chunk
            logger.warning(f"Tree-sitter not available, using fallback for {file_path}")
            result = _fallback_parse(file_path, language, content)
            
            # Save AST visualization if requested (even for fallback)
            if save_ast and chunks_dir:
                logger.debug("Saving fallback AST data for %s", file_path)
                try:
                    saved_file = save_ast_visualization(
                        str(file_path), 
                        language, 
                        None,  # No root node for fallback
                        content, 
                        result['nodes'], 
                        chunks_dir,
                        result.get('tree_info')
                    )
                    logger.debug("Saved fallback AST: %s", saved_file)
                except Exception as e:
                    logger.error("Error saving fallback AST for %s: %s", file_path, e)
                    import traceback
                    traceback.print_exc()
            
            return result
        
        # Parse with tree-sitter
        parser = get_parser(language)
        if not parser:
            # Fallback if language not supported
            logger.warning(f"No parser available for {language}, using fallback for {file_path}")
            return _fallback_parse(file_path, language, content)
        
        tree = parser.parse(bytes(content, 'utf-8'))
        nodes = extract_nodes(tree.root_node, content, language)
        
        logger.debug("Parsed %s - Found %d semantic nodes", file_path, len(nodes))
        
        # If no nodes extracted, fallback to file-level
        if not nodes:
            logger.warning(f"No semantic nodes found in {file_path}, using file-level chunking")
            result = _fallback_parse(file_path, language, content)
        else:
            result = {
                'file_path': str(file_path),
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
            logger.debug("Saving AST for %s", file_path)
            try:
                if 'tree_info' in result and result['tree_info'].get('has_ast', False):
                    # Real AST case
                    save_ast_visualization(
                        str(file_path), 
                        language, 
                        tree.root_node, 
                        content, 
                        nodes, 
                        chunks_dir,
                        result['tree_info']
                    )
                else:
                    # Fallback case
                    save_ast_visualization(
                        str(file_path), 
                        language, 
                        None, 
                        content, 
                        result['nodes'], 
                        chunks_dir,
                        result.get('tree_info')
                    )
            except Exception as e:
                logger.warning("Could not save AST for %s: %s", file_path, e)
        
        return result
    
    except Exception as e:
        logger.error("Error parsing %s: %s", file_path, e)
        return None


def _fallback_parse(file_path: Path, language: str, content: str) -> Dict[str, Any]:
    """Fallback parsing when tree-sitter is unavailable."""
    return {
        'file_path': str(file_path),
        'language': language,
        'content': content,
        'nodes': [{
            'type': 'file',
            'name': file_path.name,
            'content': content,
            'start_line': 1,
            'end_line': len(content.splitlines()),
            'start_byte': 0,
            'end_byte': len(content.encode('utf-8'))
        }],
        'tree_info': {
            'has_ast': False,
            'fallback_reason': 'tree-sitter not available or language modules missing',
            'parser_available': TREE_SITTER_AVAILABLE
        }
    }


def get_parser(language: str) -> Optional["Parser"]:
    """Get tree-sitter parser for language."""
    global _parser_cache
    
    if not TREE_SITTER_AVAILABLE:
        return None
    
    # Return cached parser
    if language in _parser_cache:
        return _parser_cache[language]
    
    try:
        # Get language module
        lang_module = LANGUAGE_MODULES.get(language)
        if not lang_module:
            logger.warning(f"No language module available for {language}")
            return None
        
        # Handle special case for TypeScript/TSX which have different API
        if language == 'typescript':
            lang_obj = Language(lang_module.language_typescript())
        elif language == 'tsx':
            lang_obj = Language(lang_module.language_tsx())
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


def extract_nodes(root_node, content: str, language: str) -> List[Dict[str, Any]]:
    """
    Extract relevant nodes from AST.
    
    Args:
        root_node: Root node of the AST
        content: Source code content
        language: Programming language
    
    Returns:
        List of extracted nodes with metadata
    """
    target_types = NODE_TYPES.get(language, [])
    if not target_types:
        return []
    
    nodes = []
    content_bytes = content.encode('utf-8')
    
    def traverse(node):
        """Recursively traverse AST."""
        if node.type in target_types:
            # Extract node content
            node_content = content_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
            
            # Get node name if available
            node_name = get_node_name(node, content_bytes)
            
            nodes.append({
                'type': node.type,
                'name': node_name,
                'content': node_content,
                'start_line': node.start_point[0] + 1,
                'end_line': node.end_point[0] + 1,
                'start_byte': node.start_byte,
                'end_byte': node.end_byte
            })
        
        # Continue traversing children
        for child in node.children:
            traverse(child)
    
    traverse(root_node)
    return nodes


def get_node_name(node, content_bytes: bytes) -> Optional[str]:
    """Extract name from a node with language-aware and node-type-aware logic."""
    try:
        node_type = node.type
        
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


def _count_nodes(node) -> int:
    """Count total number of nodes in the AST."""
    return 1 + sum(_count_nodes(child) for child in node.children)


def _get_tree_depth(node, current_depth: int = 0) -> int:
    """Get the maximum depth of the AST."""
    if not node.children:
        return current_depth
    return max(_get_tree_depth(child, current_depth + 1) for child in node.children)
