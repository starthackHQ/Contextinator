"""
Context builder module for Contextinator.

This module provides functionality to build contextual information
for code chunks, adding metadata like file path, language, and location.
"""

from typing import Any, Dict, List, Optional

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
    
    # Add parent context first if available
    if chunk.get('parent_id') and chunk.get('parent_name'):
        parent_type = chunk.get('parent_type', 'unknown')
        parent_name = chunk.get('parent_name')
        context_parts.append(f"Parent: {parent_name} ({parent_type})")
    
    # Add file path
    if 'file_path' in chunk and chunk['file_path']:
        context_parts.append(f"File: {chunk['file_path']}")
    
    # Add language
    if 'language' in chunk and chunk['language']:
        context_parts.append(f"Language: {chunk['language']}")
    
    # Add node type (function, class, etc.)
    if 'node_type' in chunk and chunk['node_type']:
        context_parts.append(f"Type: {chunk['node_type']}")
    
    # Add symbol name if available
    if 'node_name' in chunk and chunk['node_name']:
        context_parts.append(f"Symbol: {chunk['node_name']}")
    
    # Add line range
    start_line = chunk.get('start_line')
    end_line = chunk.get('end_line')
    if start_line is not None and end_line is not None:
        context_parts.append(f"Lines: {start_line}-{end_line}")
    
    return '\n'.join(context_parts) if context_parts else ''


def build_enriched_content(chunk: Dict[str, Any], content: str) -> str:
    """
    Build enriched content by combining context metadata with code content.
    
    This creates a semantically rich representation that includes:
    - File path and location information
    - Programming language
    - Node type (class, function, etc.)
    - Symbol name
    - The actual code content
    
    This enriched content is used for embedding generation to improve
    semantic search quality by providing contextual information.
    
    Args:
        chunk: Chunk dictionary containing metadata
        content: The actual code content
    
    Returns:
        Enriched content string combining context and code
        
    Examples:
        >>> chunk = {
        ...     'file_path': 'src/auth.py',
        ...     'language': 'python',
        ...     'node_type': 'function_definition',
        ...     'node_name': 'authenticate_user',
        ...     'start_line': 10,
        ...     'end_line': 25
        ... }
        >>> content = "def authenticate_user(username, password):\\n    ..."
        >>> result = build_enriched_content(chunk, content)
        >>> 'File: src/auth.py' in result
        True
        >>> 'authenticate_user' in result
        True
    """
    context = build_context(chunk)
    
    if not context:
        # No context available, return content as-is
        return content
    
    # Combine context and content with clear separation
    return f"{context}\n\n{content}"


__all__ = ['build_context', 'build_enriched_content']
