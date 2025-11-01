"""
Search tools module for Contextinator.

This module provides comprehensive search functionality for querying ChromaDB
collections with various search strategies including semantic search, full-text
search, regex patterns, and symbol-based searches.

The main components include:
- Semantic search using embeddings and cosine similarity
- Full-text search with metadata filtering
- Regular expression pattern matching
- Symbol and file-based searches
- Hybrid search combining multiple strategies
"""

from typing import Any, Dict, List, Optional

import chromadb

from ..config import CHROMA_SERVER_URL, USE_CHROMA_SERVER, sanitize_collection_name, get_storage_path
from ..utils.logger import logger


class SearchTool:
    """
    Base class for ChromaDB search tools.
    
    Provides common functionality for connecting to ChromaDB and formatting
    search results across different search strategies.
    """
    
    def __init__(self, collection_name: str, base_dir: Optional[str] = None, repo_name: Optional[str] = None) -> None:
        """
        Initialize search tool with ChromaDB connection.
        
        Args:
            collection_name: Name of the ChromaDB collection
            base_dir: Optional base directory (for future use)
            repo_name: Optional repository name (for future use)
            
        Raises:
            RuntimeError: If ChromaDB connection fails
            ValueError: If collection doesn't exist
        """
        self.collection_name = collection_name
        self.client = self._get_client()
        self.collection = self._get_collection()
    
    def _get_client(self) -> chromadb.Client:
        """
        Get ChromaDB client (matches viewer.py pattern).
        
        Returns:
            ChromaDB client instance
            
        Raises:
            RuntimeError: If client initialization fails
        """
        try:
            if USE_CHROMA_SERVER:
                return chromadb.HttpClient(host="localhost", port=8000)
            else:
                from pathlib import Path
                db_path = str(Path.cwd() / '.chromadb')
                return chromadb.PersistentClient(path=db_path)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ChromaDB client: {e}")
    
    def _get_collection(self) -> chromadb.Collection:
        """
        Get collection by name.
        
        Returns:
            ChromaDB collection instance
            
        Raises:
            ValueError: If collection doesn't exist
        """
        try:
            safe_name = sanitize_collection_name(self.collection_name)
            return self.client.get_collection(name=safe_name)
        except Exception as e:
            raise ValueError(f"Collection '{self.collection_name}' not found: {e}")
    
    def format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format ChromaDB results into consistent structure.
        
        Args:
            results: Raw ChromaDB query results
            
        Returns:
            List of formatted result dictionaries
        """
        formatted = []
        
        # Handle different result structures
        ids = results.get('ids', [])
        documents = results.get('documents', [])
        metadatas = results.get('metadatas', [])
        
        for i, id_ in enumerate(ids):
            doc = documents[i] if i < len(documents) else ''
            meta = metadatas[i] if i < len(metadatas) else {}
            
            formatted.append({
                'id': id_,
                'content': doc,
                'metadata': meta
            })
        
        return formatted


# Import all search functions
from .full_text_search import full_text_search, hybrid_search, search_by_type
from .read_file import list_files, read_file
from .regex_search import find_function_calls, regex_search
from .semantic_search import semantic_search, semantic_search_with_context
from .symbol_search import list_symbols, symbol_search

__all__ = [
    'SearchTool',
    'find_function_calls',
    'full_text_search',
    'hybrid_search',
    'list_files',
    'list_symbols',
    'read_file',
    'regex_search',
    'search_by_type',
    'semantic_search',
    'semantic_search_with_context',
    'symbol_search',
]
