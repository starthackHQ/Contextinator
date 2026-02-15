"""
Contextinator RAG Module (v1 functionality)

Advanced semantic search and code intelligence using:
- AST-based chunking
- OpenAI embeddings
- ChromaDB vector storage
- Semantic search

For basic filesystem operations, use the primary fs_read tool instead.
"""

from .chunking import chunk_repository
from .embedding import embed_chunks
from .vectorstore import store_repository_embeddings, ChromaVectorStore
from .ingestion import AsyncIngestionService
from .tools import (
    semantic_search,
    symbol_search,
    cat_file,
    grep_search,
    analyze_structure,
)

__all__ = [
    "chunk_repository",
    "embed_chunks",
    "store_repository_embeddings",
    "ChromaVectorStore",
    "AsyncIngestionService",
    "semantic_search",
    "symbol_search",
    "cat_file",
    "grep_search",
    "analyze_structure",
]
