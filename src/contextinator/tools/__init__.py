"""
Search tools module for Contextinator.

This module provides comprehensive search functionality for querying ChromaDB
collections with various search strategies including semantic search, grep search,
regex patterns, and symbol-based searches.

The main components include:
- Semantic search using embeddings and cosine similarity
- Grep search with pattern matching
- Regular expression pattern matching
- Symbol and file-based searches
- Repository structure analysis
"""

from typing import Any, Dict, List, Optional

# Lazy import chromadb

from ..config import USE_CHROMA_SERVER, sanitize_collection_name
from ..utils.logger import logger


class SearchTool:
    """
    Base class for ChromaDB search tools.
    
    Provides common functionality for connecting to ChromaDB and formatting
    search results across different search strategies.
    """
    
    def __init__(self, collection_name: str, base_dir: Optional[str] = None, repo_name: Optional[str] = None, chromadb_dir: Optional[str] = None) -> None:
        """
        Initialize search tool with ChromaDB connection.
        
        Args:
            collection_name: Name of the ChromaDB collection
            base_dir: Optional base directory (for future use)
            repo_name: Optional repository name (for future use)
            
        Raises:
            SearchError: If ChromaDB connection fails
            ValidationError: If collection doesn't exist
        """
        from ..utils.exceptions import SearchError, ValidationError
        
        if not collection_name:
            raise ValidationError("Collection name cannot be empty", "collection_name", "non-empty string")
            
        self.collection_name = collection_name
        self.chromadb_dir = chromadb_dir
        
        try:
            self.client = self._get_client()
            self.collection = self._get_collection()
        except Exception as e:
            raise SearchError(f"Failed to initialize search tool: {e}", collection_name, "initialization")
    
    def _get_client(self):
        import chromadb
        """
        Get ChromaDB client with fallback handling.
        
        Returns:
            ChromaDB client instance
            
        Raises:
            SearchError: If client initialization fails
        """
        from ..utils.exceptions import SearchError
        
        try:
            # Try server first, fallback to local
            if USE_CHROMA_SERVER:
                try:
                    from ..config import CHROMA_SERVER_URL
                    from urllib.parse import urlparse
                    parsed_url = urlparse(CHROMA_SERVER_URL)
                    host = parsed_url.hostname or "localhost"
                    port = parsed_url.port or 8000
                    client = chromadb.HttpClient(host=host, port=port)
                    # Test connection
                    client.heartbeat()
                    return client
                except Exception as e:
                    logger.warning(f"ChromaDB server unavailable, using local storage: {e}")
                    # Fall through to local client
            
            # Use local client
            from pathlib import Path
            if self.chromadb_dir:
                db_path = str(Path(self.chromadb_dir))
            else:
                db_path = str(Path.cwd() / '.chromadb')
            return chromadb.PersistentClient(path=db_path)
            
        except Exception as e:
            raise SearchError(f"Failed to initialize ChromaDB client: {e}", self.collection_name, "client_init")
    
    def _get_collection(self):
        """
        Get collection by name with error handling.
        
        Returns:
            ChromaDB collection instance
            
        Raises:
            ValidationError: If collection doesn't exist
        """
        from ..utils.exceptions import ValidationError
        
        try:
            safe_name = sanitize_collection_name(self.collection_name)
            return self.client.get_collection(name=safe_name)
        except Exception as e:
            raise ValidationError(f"Collection '{self.collection_name}' not found: {e}", "collection_name", "existing collection")
    
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


# Import all search functions (all async now)
from .cat_file import cat_file
from .grep_search import grep_search, find_function_calls
from .repo_structure import analyze_structure, analyze_structure_async
from .semantic_search import semantic_search, semantic_search_with_context
from .symbol_search import list_symbols, symbol_search

__all__ = [
    'SearchTool',
    'analyze_structure',
    'analyze_structure_async',
    'cat_file',
    'find_function_calls',
    'grep_search',
    'list_symbols',
    'semantic_search',
    'semantic_search_with_context',
    'symbol_search',
]
