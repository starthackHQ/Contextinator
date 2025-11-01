"""Search tools for querying ChromaDB collections."""
from typing import List, Dict, Any, Optional
import chromadb
from ..config import sanitize_collection_name, USE_CHROMA_SERVER, CHROMA_SERVER_URL


class SearchTool:
    """Base class for ChromaDB search tools."""
    
    def __init__(self, collection_name: str, base_dir: Optional[str] = None, repo_name: Optional[str] = None):
        """Initialize search tool with ChromaDB connection."""
        self.collection_name = collection_name
        self.client = self._get_client()
        self.collection = self._get_collection()
    
    def _get_client(self):
        """Get ChromaDB client (matches viewer.py pattern)."""
        if USE_CHROMA_SERVER:
            return chromadb.HttpClient(host="localhost", port=8000)
        else:
            from ..config import get_storage_path
            from pathlib import Path
            db_path = str(Path.cwd() / '.chromadb')
            return chromadb.PersistentClient(path=db_path)
    
    def _get_collection(self):
        """Get collection by name."""
        safe_name = sanitize_collection_name(self.collection_name)
        return self.client.get_collection(name=safe_name)
    
    def format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format ChromaDB results into consistent structure."""
        formatted = []
        for id_, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
            formatted.append({
                'id': id_,
                'content': doc,
                'metadata': meta
            })
        return formatted


# Import all search functions
from .symbol_search import symbol_search, list_symbols
from .regex_search import regex_search, find_function_calls
from .read_file import read_file, list_files
from .semantic_search import semantic_search, semantic_search_with_context
from .full_text_search import full_text_search, hybrid_search, search_by_type

__all__ = [
    'SearchTool',
    'symbol_search',
    'list_symbols',
    'regex_search',
    'find_function_calls',
    'read_file',
    'list_files',
    'semantic_search',
    'semantic_search_with_context',
    'full_text_search',
    'hybrid_search',
    'search_by_type',
]
