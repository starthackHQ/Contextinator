"""
AST Visualizer for Contextinator

This module provides functionality to visualize and save AST trees
created by tree-sitter for understanding the parsing and chunking process.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..config import CHUNKS_DIR
from ..utils.logger import logger


def serialize_node(node, content_bytes: bytes, max_depth: int = None, current_depth: int = 0) -> Dict[str, Any]:
    """
    Serialize a tree-sitter node to a dictionary for JSON serialization.
    
    Args:
        node: Tree-sitter node
        content_bytes: Source code as bytes
        max_depth: Maximum depth to traverse (None for unlimited)
        current_depth: Current traversal depth
    
    Returns:
        Dictionary representation of the node
    """
    if max_depth is not None and current_depth >= max_depth:
        return {
            'type': node.type,
            'text': '... (max depth reached)',
            'start_point': node.start_point,
            'end_point': node.end_point,
            'start_byte': node.start_byte,
            'end_byte': node.end_byte,
            'children_count': len(node.children)
        }
    
    # Get node text (truncate if too long)
    node_text = content_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
    if len(node_text) > 200:
        node_text = node_text[:200] + '...'
    
    node_dict = {
        'type': node.type,
        'text': node_text,
        'start_point': {
            'row': node.start_point[0],
            'column': node.start_point[1]
        },
        'end_point': {
            'row': node.end_point[0],
            'column': node.end_point[1]
        },
        'start_byte': node.start_byte,
        'end_byte': node.end_byte,
        'is_named': node.is_named,
        'children': []
    }
    
    # Recursively serialize children
    for child in node.children:
        child_dict = serialize_node(child, content_bytes, max_depth, current_depth + 1)
        node_dict['children'].append(child_dict)
    
    return node_dict


def create_ast_summary(root_node, content_bytes: bytes) -> Dict[str, Any]:
    """
    Create a summary of the AST structure.
    
    Args:
        root_node: Root node of the AST
        content_bytes: Source code as bytes
    
    Returns:
        AST summary dictionary
    """
    def count_nodes_by_type(node, counts=None):
        if counts is None:
            counts = {}
        
        counts[node.type] = counts.get(node.type, 0) + 1
        for child in node.children:
            count_nodes_by_type(child, counts)
        
        return counts
    
    def get_tree_depth(node, current_depth=0):
        if not node.children:
            return current_depth
        return max(get_tree_depth(child, current_depth + 1) for child in node.children)
    
    node_counts = count_nodes_by_type(root_node)
    
    return {
        'total_nodes': sum(node_counts.values()),
        'max_depth': get_tree_depth(root_node),
        'node_type_distribution': dict(sorted(node_counts.items(), key=lambda x: x[1], reverse=True)),
        'root_type': root_node.type,
        'tree_size_bytes': root_node.end_byte - root_node.start_byte
    }


def save_ast_visualization(file_path: str, language: str, root_node, content: str, 
                          extracted_nodes: List[Dict[str, Any]], chunks_dir: Path,
                          tree_info: Dict[str, Any] = None):
    """
    Save AST visualization data to files.
    
    Args:
        file_path: Path to the source file
        language: Programming language
        root_node: Root node of the AST (can be None for fallback cases)
        content: Source code content
        extracted_nodes: List of extracted semantic nodes
        chunks_dir: Chunks directory (repository-specific) for saving AST data
        tree_info: Tree information including whether AST is available
    """
    ast_dir = chunks_dir / 'ast_trees'
    ast_dir.mkdir(parents=True, exist_ok=True)
    
    content_bytes = content.encode('utf-8')
    file_stem = Path(file_path).stem
    
    # Create comprehensive AST data
    ast_data = {
        'file_info': {
            'path': file_path,
            'language': language,
            'size_bytes': len(content_bytes),
            'line_count': len(content.splitlines())
        },
        'tree_info': tree_info or {'has_ast': False, 'fallback_reason': 'unknown'},
        'extracted_nodes': extracted_nodes
    }
    
    # Only add AST-specific data if we have a real AST
    if root_node and tree_info and tree_info.get('has_ast', False):
        ast_data['ast_summary'] = create_ast_summary(root_node, content_bytes)
        ast_data['full_ast'] = serialize_node(root_node, content_bytes, max_depth=10)
        ast_data['extraction_mapping'] = create_extraction_mapping(root_node, extracted_nodes, content_bytes)
    else:
        ast_data['ast_summary'] = {
            'total_nodes': 0,
            'max_depth': 0,
            'node_type_distribution': {},
            'tree_size_bytes': len(content_bytes),
            'fallback_used': True
        }
        ast_data['full_ast'] = None
        ast_data['extraction_mapping'] = {
            'fallback_mode': True,
            'extracted_count': len(extracted_nodes),
            'note': 'File-level chunking used due to tree-sitter unavailability'
        }
    
    # Save to JSON file
    output_file = ast_dir / f'{file_stem}_{language}_ast.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ast_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"AST saved: {output_file}")
    return output_file


def create_extraction_mapping(root_node, extracted_nodes: List[Dict[str, Any]], content_bytes: bytes) -> Dict[str, Any]:
    """
    Create a mapping showing how extracted nodes relate to the full AST.
    
    Args:
        root_node: Root node of the AST
        extracted_nodes: List of extracted semantic nodes
        content_bytes: Source code as bytes
    
    Returns:
        Mapping dictionary
    """
    def find_node_path(node, target_start_byte, target_end_byte, path=None):
        if path is None:
            path = []
        
        if node.start_byte == target_start_byte and node.end_byte == target_end_byte:
            return path + [{'type': node.type, 'byte_range': [node.start_byte, node.end_byte]}]
        
        for i, child in enumerate(node.children):
            if child.start_byte <= target_start_byte and child.end_byte >= target_end_byte:
                result = find_node_path(
                    child, 
                    target_start_byte, 
                    target_end_byte, 
                    path + [{'type': node.type, 'child_index': i, 'byte_range': [node.start_byte, node.end_byte]}]
                )
                if result:
                    return result
        
        return None
    
    mapping = {
        'total_ast_nodes': count_total_nodes(root_node),
        'extracted_count': len(extracted_nodes),
        'extraction_paths': []
    }
    
    for extracted in extracted_nodes:
        path = find_node_path(root_node, extracted['start_byte'], extracted['end_byte'])
        mapping['extraction_paths'].append({
            'extracted_node': {
                'type': extracted['type'],
                'name': extracted.get('name'),
                'byte_range': [extracted['start_byte'], extracted['end_byte']],
                'line_range': [extracted['start_line'], extracted['end_line']]
            },
            'ast_path': path or 'Not found'
        })
    
    return mapping


def count_total_nodes(node) -> int:
    """Count total number of nodes in the AST."""
    return 1 + sum(count_total_nodes(child) for child in node.children)


def create_ast_overview(chunks_dir: Path) -> Dict[str, Any]:
    """
    Create an overview of all AST files in the chunks directory.
    
    Args:
        chunks_dir: Repository-specific chunks directory containing AST files
    
    Returns:
        Overview dictionary
    """
    ast_dir = chunks_dir / 'ast_trees'
    
    if not ast_dir.exists():
        return {
            'error': 'No AST directory found',
            'note': 'AST directory is created when --save-ast flag is used during chunking'
        }
    
    overview = {
        'total_files': 0,
        'languages': {},
        'total_nodes_extracted': 0,
        'total_ast_nodes': 0,
        'tree_sitter_available': False,
        'fallback_files': 0,
        'real_ast_files': 0,
        'files': []
    }
    
    for ast_file in ast_dir.glob('*_ast.json'):
        try:
            with open(ast_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            lang = data['file_info']['language']
            overview['languages'][lang] = overview['languages'].get(lang, 0) + 1
            overview['total_files'] += 1
            overview['total_nodes_extracted'] += len(data['extracted_nodes'])
            
            # Check if this file used real AST or fallback
            tree_info = data.get('tree_info', {})
            has_ast = tree_info.get('has_ast', False)
            
            if has_ast:
                overview['real_ast_files'] += 1
                overview['tree_sitter_available'] = True
                overview['total_ast_nodes'] += data['ast_summary']['total_nodes']
            else:
                overview['fallback_files'] += 1
            
            overview['files'].append({
                'file': data['file_info']['path'],
                'language': lang,
                'ast_nodes': data['ast_summary']['total_nodes'] if has_ast else 0,
                'extracted_nodes': len(data['extracted_nodes']),
                'tree_depth': data['ast_summary'].get('max_depth', 0) if has_ast else 0,
                'has_real_ast': has_ast,
                'fallback_reason': tree_info.get('fallback_reason') if not has_ast else None
            })
            
        except Exception as e:
            logger.info(f"Error reading {ast_file}: {e}")
    
    return overview


def save_ast_overview(chunks_dir: Path):
    """
    Save AST overview to a summary file.
    
    Args:
        chunks_dir: Repository-specific chunks directory
    """
    overview = create_ast_overview(chunks_dir)
    
    ast_dir = chunks_dir / 'ast_trees'
    ast_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    overview_file = ast_dir / 'ast_overview.json'
    
    with open(overview_file, 'w', encoding='utf-8') as f:
        json.dump(overview, f, indent=2, ensure_ascii=False)
    
    logger.info(f"📈 AST overview saved: {overview_file}")
    return overview

__all__ = [
    'save_ast_overview',
    'save_ast_visualization', 
    'serialize_node',
]
