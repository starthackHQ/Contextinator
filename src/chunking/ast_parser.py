from pathlib import Path
from typing import Optional, Dict, Any, List
from ..config import SUPPORTED_EXTENSIONS

try:
    from tree_sitter import Parser
    from .tree_sitter_setup import get_language, setup_tree_sitter_languages
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


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
}

# Cache for parsers
_parser_cache = {}
_setup_attempted = False


def parse_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Parse a file and return its AST representation with extracted nodes.
    
    Args:
        file_path: Path to the file to parse
    
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
            return _fallback_parse(file_path, language, content)
        
        # Parse with tree-sitter
        parser = get_parser(language)
        if not parser:
            # Fallback if language not supported
            return _fallback_parse(file_path, language, content)
        
        tree = parser.parse(bytes(content, 'utf-8'))
        nodes = extract_nodes(tree.root_node, content, language)
        
        # If no nodes extracted, fallback to file-level
        if not nodes:
            return _fallback_parse(file_path, language, content)
        
        return {
            'file_path': str(file_path),
            'language': language,
            'content': content,
            'nodes': nodes
        }
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
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
        }]
    }


def get_parser(language: str) -> Optional[Parser]:
    """Get tree-sitter parser for language."""
    global _setup_attempted, _parser_cache
    
    if not TREE_SITTER_AVAILABLE:
        return None
    
    # Return cached parser
    if language in _parser_cache:
        return _parser_cache[language]
    
    # Setup tree-sitter on first use
    if not _setup_attempted:
        _setup_attempted = True
        setup_tree_sitter_languages()
    
    try:
        lang_obj = get_language(language)
        if not lang_obj:
            return None
        
        parser = Parser()
        parser.set_language(lang_obj)
        _parser_cache[language] = parser
        return parser
        
    except Exception:
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
    """Extract name from a node (function/class name)."""
    try:
        # Look for identifier child
        for child in node.children:
            if child.type == 'identifier' or child.type == 'name':
                return content_bytes[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
        return None
    except Exception:
        return None
