from typing import List, Dict, Any
from ..utils import count_tokens
from ..config import MAX_TOKENS, CHUNK_OVERLAP


def split_chunk(chunk: Dict[str, Any], max_tokens: int = MAX_TOKENS, overlap: int = CHUNK_OVERLAP) -> List[Dict[str, Any]]:
    """
    Split a large chunk into smaller chunks based on token limit.
    
    Args:
        chunk: Chunk dictionary with 'content' key
        max_tokens: Maximum tokens per chunk
        overlap: Number of tokens to overlap between chunks
    
    Returns:
        List of split chunks
    """
    content = chunk['content']
    lines = content.splitlines()
    
    # If chunk is small enough, return as-is
    if count_tokens(content) <= max_tokens:
        return [chunk]
    
    splits = []
    current_split = []
    current_tokens = 0
    
    for line in lines:
        line_tokens = count_tokens(line)
        
        if current_tokens + line_tokens > max_tokens and current_split:
            # Flush current split
            split_content = '\n'.join(current_split)
            splits.append(_create_split_chunk(chunk, split_content, len(splits)))
            
            # Reset with overlap
            overlap_lines = _get_overlap_lines(current_split, overlap)
            current_split = overlap_lines
            current_tokens = sum(count_tokens(l) for l in overlap_lines)
        
        current_split.append(line)
        current_tokens += line_tokens
    
    # Add remaining lines
    if current_split:
        split_content = '\n'.join(current_split)
        splits.append(_create_split_chunk(chunk, split_content, len(splits)))
    
    return splits if splits else [chunk]


def _create_split_chunk(original_chunk: Dict[str, Any], content: str, split_index: int) -> Dict[str, Any]:
    """Create a new chunk from a split."""
    return {
        **original_chunk,
        'content': content,
        'is_split': True,
        'split_index': split_index,
        'original_hash': original_chunk.get('hash')
    }


def _get_overlap_lines(lines: List[str], overlap_tokens: int) -> List[str]:
    """Get last N lines that fit within overlap token limit."""
    overlap_lines = []
    tokens = 0
    
    for line in reversed(lines):
        line_tokens = count_tokens(line)
        if tokens + line_tokens > overlap_tokens:
            break
        overlap_lines.insert(0, line)
        tokens += line_tokens
    
    return overlap_lines
