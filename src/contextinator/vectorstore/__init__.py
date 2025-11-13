"""
Vector store module for Contextinator.

This module provides functionality for storing and managing code embeddings
in vector databases, with ChromaDB as the primary implementation.
"""

from .chroma_store import (
    ChromaVectorStore,
    get_repository_collection_info,
    store_repository_embeddings,
)

__all__ = [
    'ChromaVectorStore',
    'get_repository_collection_info',
    'store_repository_embeddings',
]
