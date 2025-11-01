"""
Context builder module for Contextinator.

This module provides functionality to build contextual information
for code chunks, adding metadata like file path, language, and location.
"""

from typing import Any, Dict, List


def build_context(chunk: Dict[str, Any]) -> str:
    """
    Build contextual information for a chunk.
    
    Creates a formatted context string containing metadata about the chunk
    such as file path, programming language, node type, and line numbers.
    
    Args:
        chunk: Chunk dictionary containing metadata
    
    Returns:
        Context string to prepend to chunk content
        
    Raises:
        TypeError: If chunk is not a dictionary
        
    Examples:
        >>> chunk = {
        ...     'file_path': 'src/main.py',
        ...     'language': 'python',
        ...     'node_type': 'function',
        ...     'start_line': 10,
        ...     'end_line': 20
        ... }
        >>> build_context(chunk)
        'File: src/main.py\\nLanguage: python\\nType: function\\nLines: 10-20'
    """
    if not isinstance(chunk, dict):
        raise TypeError("Chunk must be a dictionary")
        
    context_parts: List[str] = []
    
    # Add file path
    if 'file_path' in chunk and chunk['file_path']:
        context_parts.append(f"File: {chunk['file_path']}")
    
    # Add language
    if 'language' in chunk and chunk['language']:
        context_parts.append(f"Language: {chunk['language']}")
    
    # Add node type (function, class, etc.)
    if 'node_type' in chunk and chunk['node_type']:
        context_parts.append(f"Type: {chunk['node_type']}")
    
    # Add line range
    start_line = chunk.get('start_line')
    end_line = chunk.get('end_line')
    if start_line is not None and end_line is not None:
        context_parts.append(f"Lines: {start_line}-{end_line}")
    
    return '\n'.join(context_parts) if context_parts else ''


__all__ = ['build_context']
