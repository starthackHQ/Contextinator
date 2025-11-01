"""
Contextinator: Intelligent Codebase Understanding for AI Agents.

Transform any codebase into semantically-aware, searchable knowledge 
for AI-powered workflows using AST parsing and vector embeddings.
"""

from typing import List

__version__ = "0.1.0"
__author__ = "Contextinator Team"
__email__ = "contact@contextinator.dev"

# Core functionality exports
from .chunking import chunk_repository
from .embedding import embed_chunks
from .vectorstore import store_repository_embeddings
from .tools import semantic_search, full_text_search

__all__ = [
    "__version__",
    "chunk_repository", 
    "embed_chunks",
    "store_repository_embeddings",
    "semantic_search",
    "full_text_search",
]