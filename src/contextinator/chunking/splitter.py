"""
Chunk splitter module for Contextinator.

This module provides functionality to split large code chunks into smaller
pieces based on token limits while maintaining context through overlapping content.
"""

import uuid
from typing import Any, Dict, List

from ..config import CHUNK_OVERLAP, MAX_TOKENS
from ..utils import count_tokens
from ..utils.logger import logger


def split_chunk(
    chunk: Dict[str, Any], 
    max_tokens: int = MAX_TOKENS, 
    overlap: int = CHUNK_OVERLAP
) -> List[Dict[str, Any]]:
    """
    Split a large chunk into smaller chunks based on token limit.
    
    Splits content by lines while maintaining context through overlapping
    content between adjacent chunks. Preserves all original metadata.
    
    Args:
        chunk: Chunk dictionary with 'content' key and metadata
        max_tokens: Maximum tokens per chunk (default from config)
        overlap: Number of tokens to overlap between chunks (default from config)
    
    Returns:
        List of split chunks, or original chunk if splitting not needed
        
    Raises:
        TypeError: If chunk is not a dictionary
        ValueError: If max_tokens or overlap are invalid
        KeyError: If chunk missing required 'content' key
        
    Examples:
        >>> chunk = {'content': 'very long code...', 'file_path': 'test.py'}
        >>> splits = split_chunk(chunk, max_tokens=100, overlap=10)
        >>> len(splits)  # Number of chunks created
        3
    """
    if not isinstance(chunk, dict):
        raise TypeError("Chunk must be a dictionary")
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= max_tokens:
        raise ValueError("overlap must be less than max_tokens")
    if 'content' not in chunk:
        raise KeyError("Chunk must contain 'content' key")
    
    content = chunk['content']
    if not content:
        logger.debug("Empty content, returning original chunk")
        return [chunk]
        
    lines = content.splitlines()
    
    # If chunk is small enough, return as-is
    total_tokens = count_tokens(content)
    if total_tokens <= max_tokens:
        logger.debug(f"Chunk fits in {total_tokens} tokens, no splitting needed")
        return [chunk]
    
    logger.debug(f"Splitting chunk with {total_tokens} tokens into max {max_tokens} token pieces")
    
    splits = []
    current_split = []
    current_tokens = 0
    
    for line in lines:
        line_tokens = count_tokens(line)
        
        # Check if adding this line would exceed the limit
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
    
    logger.debug(f"Split into {len(splits)} chunks")
    return splits if splits else [chunk]


def _create_split_chunk(original_chunk: Dict[str, Any], content: str, split_index: int) -> Dict[str, Any]:
    """
    Create a new chunk from a split with preserved metadata.
    
    BUGFIX: Generate unique ID for each split chunk to prevent duplicate IDs in ChromaDB.
    
    Args:
        original_chunk: Original chunk dictionary
        content: New content for the split
        split_index: Index of this split (0-based)
        
    Returns:
        New chunk dictionary with split metadata and unique ID
    """
    from .context_builder import build_enriched_content
    
    # Create base metadata for the split (exclude 'id' to generate new unique ID)
    chunk_metadata = {k: v for k, v in original_chunk.items() 
                      if k not in ['content', 'enriched_content', 'is_split', 'split_index', 'original_hash', 'token_count', 'id']}
    
    # Build enriched content for the split chunk
    enriched_content = build_enriched_content(chunk_metadata, content)
    
    # Generate unique ID for each split chunk (BUGFIX: prevents duplicate IDs)
    split_id = str(uuid.uuid4())
    
    return {
        **original_chunk,
        'id': split_id,  # NEW UNIQUE ID for split chunk
        'original_id': original_chunk.get('id'),  # Preserve original ID for reference
        'content': content,
        'enriched_content': enriched_content,  # Rebuild enriched content for split
        'is_split': True,
        'split_index': split_index,
        'original_hash': original_chunk.get('hash'),
        'token_count': count_tokens(content)
    }


def _get_overlap_lines(lines: List[str], overlap_tokens: int) -> List[str]:
    """
    Get last N lines that fit within overlap token limit.
    
    Selects lines from the end of the current split to include
    as context at the beginning of the next split.
    
    Args:
        lines: List of lines from current split
        overlap_tokens: Maximum tokens for overlap content
        
    Returns:
        List of lines to use as overlap context
    """
    if overlap_tokens <= 0 or not lines:
        return []
        
    overlap_lines = []
    tokens = 0
    
    # Work backwards from the end
    for line in reversed(lines):
        line_tokens = count_tokens(line)
        if tokens + line_tokens > overlap_tokens:
            break
        overlap_lines.insert(0, line)
        tokens += line_tokens
    
    return overlap_lines


__all__ = [
    'split_chunk',
]
