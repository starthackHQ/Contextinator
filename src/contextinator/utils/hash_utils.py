"""
Content hashing utilities for Contextinator.

This module provides functions for generating content hashes used in
deduplication and content identification.
"""

import hashlib


def hash_content(content: str) -> str:
    """
    Generate SHA256 hash of content for deduplication.
    
    Args:
        content: String content to hash
        
    Returns:
        Hexadecimal SHA256 hash string
        
    Raises:
        TypeError: If content is not a string
    """
    if not isinstance(content, str):
        raise TypeError("Content must be a string")
        
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


__all__ = ['hash_content']
