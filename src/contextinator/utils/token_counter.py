"""
Token counting utilities for Contextinator.

This module provides functions for counting tokens in text using tiktoken,
OpenAI's official tokenizer, ensuring accurate token counts for chunking.
"""

from functools import lru_cache

import tiktoken

from .logger import logger


@lru_cache(maxsize=8)
def _get_encoding(model: str) -> tiktoken.Encoding:
    """
    Get tiktoken encoding for a model with caching.
    
    Args:
        model: Model name (e.g., 'text-embedding-3-large', 'gpt-4')
    
    Returns:
        tiktoken.Encoding object
        
    Raises:
        ValueError: If model is empty or None
    """
    if not model:
        raise ValueError("Model name cannot be empty")
        
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base encoding (used by GPT-4, GPT-3.5-turbo, text-embedding-3-*)
        logger.warning(f"Model '{model}' not found in tiktoken, using cl100k_base encoding")
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str, model: str = "text-embedding-3-large") -> int:
    """
    Count tokens in text using tiktoken (OpenAI's official tokenizer).
    
    This uses BPE (Byte Pair Encoding) tokenization which accurately matches
    how OpenAI models tokenize text, ensuring chunk sizes stay within limits.
    
    Args:
        text: Text to count tokens for
        model: Model name to use for tokenization (default: text-embedding-3-large)
               Matches the embedding model used in embedding_service.py
    
    Returns:
        Number of tokens in the text
        
    Raises:
        TypeError: If text is not a string
        ValueError: If model is empty or None
    
    Examples:
        >>> count_tokens("Hello world")
        2
        >>> count_tokens("def hello():\\n    pass", model="gpt-4")
        8
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
        
    if not text:
        return 0
    
    encoding = _get_encoding(model)
    return len(encoding.encode(text))


__all__ = ['count_tokens']
