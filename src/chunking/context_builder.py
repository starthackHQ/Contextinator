from typing import Dict, Any


def build_context(chunk: Dict[str, Any]) -> str:
    """
    Build contextual information for a chunk.
    
    Args:
        chunk: Chunk dictionary
    
    Returns:
        Context string to prepend to chunk content
    """
    context_parts = []
    
    # Add file path
    if 'file_path' in chunk:
        context_parts.append(f"File: {chunk['file_path']}")
    
    # Add language
    if 'language' in chunk:
        context_parts.append(f"Language: {chunk['language']}")
    
    # Add node type (function, class, etc.)
    if 'node_type' in chunk:
        context_parts.append(f"Type: {chunk['node_type']}")
    
    # Add line range
    if 'start_line' in chunk and 'end_line' in chunk:
        context_parts.append(f"Lines: {chunk['start_line']}-{chunk['end_line']}")
    
    return '\n'.join(context_parts) if context_parts else ''
