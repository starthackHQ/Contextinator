"""
Contextinator: Intelligent Codebase Understanding for AI Agents.

Transform any codebase into semantically-aware, searchable knowledge 
for AI-powered workflows using AST parsing and vector embeddings.
"""

try:
    #  the _version.py file is auto-generated when you build the package.
    from ._version import version as __version__
except ImportError:
    # when in dev
    __version__ = "0.0.0+unknown"



# Core functionality exports
from .chunking import chunk_repository
from .embedding import embed_chunks
from .vectorstore import store_repository_embeddings, ChromaVectorStore
from .tools import semantic_search, symbol_search, cat_file, grep_search, find_function_calls
from .ingestion import AsyncIngestionService

__all__ = [
    "__version__",
    "chunk_repository",
    "embed_chunks",
    "store_repository_embeddings",
    "semantic_search",
    "symbol_search",
    "cat_file",
    "grep_search",
    "find_function_calls",
    "ChromaVectorStore",
    "AsyncIngestionService",
]
