"""
Embedding module for Contextinator.

This module provides functionality for generating embeddings from code chunks
using OpenAI's embedding API, with support for batch processing, validation,
and persistent storage.
"""

from .embedding_service import (
    EmbeddingService,
    embed_chunks,
    load_chunks,
    load_embeddings,
    save_embeddings,
)

__all__ = [
    'EmbeddingService',
    'embed_chunks',
    'load_chunks',
    'load_embeddings',
    'save_embeddings',
]
