"""
Semantic search module for Contextinator.

This module provides natural language code search functionality using embeddings
and cosine similarity for finding semantically similar code chunks.
"""

from typing import Any, Dict, List, Optional, Set

from . import SearchTool
from ..utils.logger import logger

# Cache for embedding service to avoid repeated initialization
_embedding_service_cache: Optional[Any] = None


def _get_embedding_service():
    """
    Get cached EmbeddingService instance, creating it if needed.
    
    Returns:
        Cached EmbeddingService instance
    """
    global _embedding_service_cache
    if _embedding_service_cache is None:
        from ..embedding.embedding_service import EmbeddingService
        _embedding_service_cache = EmbeddingService()
    return _embedding_service_cache


def semantic_search(
    collection_name: str,
    query: str,
    n_results: int = 5,
    language: Optional[str] = None,
    file_path: Optional[str] = None,
    node_type: Optional[str] = None,
    include_parents: bool = False,
    chromadb_dir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for semantically similar code using natural language queries.
    
    Uses cosine similarity for vector comparison to find code chunks that are
    semantically similar to the natural language query.
    
    Args:
        collection_name: ChromaDB collection name
        query: Natural language query (e.g., "How is authentication handled?")
        n_results: Number of results to return (default: 5)
        language: Optional filter by programming language
        file_path: Optional filter by file path (partial match)
        node_type: Optional filter by node type (function, class, etc.)
        include_parents: Include parent chunks (classes/modules) in results (default: False)
    
    Returns:
        List of most relevant chunks with cosine similarity scores
        
    Raises:
        ValidationError: If collection_name or query is empty
        SearchError: If search fails
    
    Examples:
        >>> # Find authentication logic
        >>> semantic_search("my-repo", "How is authentication handled?")
        
        >>> # Find error handling in Python
        >>> semantic_search("my-repo", "error handling patterns", language="python")
        
        >>> # Find database logic in specific file
        >>> semantic_search("my-repo", "database connection", file_path="db.py")
    """
    from ..utils.exceptions import ValidationError, SearchError
    
    if not collection_name:
        raise ValidationError("Collection name cannot be empty", "collection_name", "non-empty string")
    if not query:
        raise ValidationError("Query cannot be empty", "query", "non-empty string")
    if n_results <= 0:
        raise ValidationError("n_results must be positive", "n_results", "positive integer")
    
    logger.debug(f"Semantic search: '{query}' in collection '{collection_name}'")
    
    try:
        # Pattern 2: Handle missing collection gracefully
        try:
            tool = SearchTool(collection_name, chromadb_dir=chromadb_dir)
        except ValueError as e:
            # Collection doesn't exist
            logger.warning(f"Collection '{collection_name}' not found: {e}")
            return []
        
        # Build where clause for metadata filters
        where = {}
        if language:
            where["language"] = language
        if file_path:
            where["file_path"] = {"$contains": file_path}
        if node_type:
            where["node_type"] = node_type
        
        # Filter parents by default (unless explicitly included)
        if not include_parents:
            where["is_parent"] = False
        
        # Generate OpenAI embeddings for the query using cached service
        embedding_service = _get_embedding_service()
        
        # Create enriched query with context for better matching
        # For queries, we add language context if specified
        enriched_query = query
        if language:
            enriched_query = f"Language: {language}\n\n{query}"
        
        query_chunk = [{'content': enriched_query}]
        query_result = embedding_service.generate_embeddings(query_chunk)[0]
        query_embedding = query_result['embedding']
        
        # ChromaDB uses cosine similarity by default for query
        results = tool.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where if where else None,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Handle empty results
        if not results or not results.get('ids') or not results['ids'][0]:
            logger.debug("No semantic matches found")
            return []
        
        # Format results with cosine similarity scores
        # ChromaDB returns distances, convert to cosine similarity: similarity = 1 - distance
        formatted = []
        for id_, doc, meta, distance in zip(
            results['ids'][0],
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            formatted.append({
                'id': id_,
                'content': doc,
                'metadata': meta,
                'distance': distance,
                'cosine_similarity': 1 - distance
            })
        
        logger.debug(f"Found {len(formatted)} semantic matches")
        return formatted
        
    except (ValidationError, SearchError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise SearchError(f"Semantic search failed: {e}", query, "semantic")


def semantic_search_with_context(
    collection_name: str,
    query: str,
    n_results: int = 3,
    **filters: Any
) -> Dict[str, Any]:
    """
    Semantic search with additional context about results.
    
    Performs semantic search and provides additional context information
    about the results including files, languages, and node types found.
    
    Args:
        collection_name: ChromaDB collection name
        query: Natural language query
        n_results: Number of results to return (default: 3)
        **filters: Additional metadata filters (language, file_path, node_type)
    
    Returns:
        Dictionary with results and context information
        
    Raises:
        ValueError: If collection_name or query is empty
        RuntimeError: If search fails
        
    Examples:
        >>> result = semantic_search_with_context("my-repo", "authentication")
        >>> print(f"Found {result['total_results']} results")
        >>> print(f"Files: {result['context']['files']}")
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if not query:
        raise ValueError("Query cannot be empty")
    
    try:
        results = semantic_search(collection_name, query, n_results, **filters)
        
        # Extract context information
        files: Set[Optional[str]] = {r['metadata'].get('file_path') for r in results}
        languages: Set[Optional[str]] = {r['metadata'].get('language') for r in results}
        node_types: Set[Optional[str]] = {r['metadata'].get('node_type') for r in results}
        
        # Filter out None values and sort
        context = {
            'files': sorted([f for f in files if f is not None]),
            'languages': sorted([l for l in languages if l is not None]),
            'node_types': sorted([nt for nt in node_types if nt is not None])
        }
        
        return {
            'query': query,
            'total_results': len(results),
            'results': results,
            'context': context,
            'filters_applied': filters
        }
        
    except Exception as e:
        logger.error(f"Semantic search with context failed: {e}")
        raise RuntimeError(f"Semantic search with context failed: {e}")


__all__ = [
    'semantic_search',
    'semantic_search_with_context',
]
