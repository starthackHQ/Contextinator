"""
Full text search module for Contextinator.

This module provides advanced multi-criteria search functionality combining
text patterns with metadata filters for precise code discovery.
"""

from typing import Any, Dict, List, Optional

from . import SearchTool
from ..utils.logger import logger


def full_text_search(
    collection_name: str,
    text_pattern: Optional[str] = None,
    where: Optional[Dict[str, Any]] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Advanced search with flexible metadata filtering.
    
    Combines text pattern matching with metadata filters to provide
    precise search capabilities across code chunks.
    
    Args:
        collection_name: ChromaDB collection name
        text_pattern: Optional text pattern to search in content
        where: ChromaDB where clause for metadata filtering
        limit: Maximum results to return (default: 50)
    
    Returns:
        List of matching chunks with metadata
        
    Raises:
        ValueError: If collection_name is empty or limit is non-positive
        RuntimeError: If search fails
    
    Examples:
        >>> # Find all imports in auth.ts
        >>> full_text_search("my-repo", 
        ...     text_pattern="import",
        ...     where={"file_path": {"$contains": "auth.ts"}})
        
        >>> # Get all Python functions in utils directory
        >>> full_text_search("my-repo",
        ...     where={"language": "python", "node_type": "function"})
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if limit <= 0:
        raise ValueError("Limit must be positive")
    
    logger.debug(f"Full text search in collection '{collection_name}'")
    
    try:
        tool = SearchTool(collection_name)
        
        if text_pattern:
            # Use ChromaDB's get method with where clause for text search
            results = tool.collection.get(
                where=where,
                limit=limit,
                include=['documents', 'metadatas']
            )
            
            # Filter by text pattern manually (ChromaDB doesn't have built-in text search)
            filtered_results = {
                'ids': [],
                'documents': [],
                'metadatas': []
            }
            
            for id_, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
                if text_pattern.lower() in doc.lower():
                    filtered_results['ids'].append(id_)
                    filtered_results['documents'].append(doc)
                    filtered_results['metadatas'].append(meta)
            
            results = filtered_results
        else:
            # Just metadata filtering
            results = tool.collection.get(
                where=where,
                limit=limit,
                include=['documents', 'metadatas']
            )
        
        formatted = tool.format_results(results)
        logger.debug(f"Found {len(formatted)} matches")
        return formatted
        
    except Exception as e:
        logger.error(f"Full text search failed: {e}")
        raise RuntimeError(f"Full text search failed: {e}")


def hybrid_search(
    collection_name: str,
    semantic_query: Optional[str] = None,
    text_pattern: Optional[str] = None,
    where: Optional[Dict[str, Any]] = None,
    n_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Hybrid search combining semantic and text-based search.
    
    Args:
        collection_name: ChromaDB collection name
        semantic_query: Natural language query for semantic search
        text_pattern: Text pattern for exact matching
        where: Metadata filters
        n_results: Number of results to return
        
    Returns:
        Combined and deduplicated search results
        
    Raises:
        ValueError: If collection_name is empty or no search criteria provided
        RuntimeError: If search fails
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if not semantic_query and not text_pattern:
        raise ValueError("Either semantic_query or text_pattern must be provided")
    
    try:
        results = []
        seen_ids = set()
        
        # Semantic search if query provided
        if semantic_query:
            from .semantic_search import semantic_search
            semantic_results = semantic_search(
                collection_name, semantic_query, n_results, **where or {}
            )
            for result in semantic_results:
                if result['id'] not in seen_ids:
                    result['search_type'] = 'semantic'
                    results.append(result)
                    seen_ids.add(result['id'])
        
        # Text search if pattern provided
        if text_pattern:
            text_results = full_text_search(
                collection_name, text_pattern, where, n_results
            )
            for result in text_results:
                if result['id'] not in seen_ids:
                    result['search_type'] = 'text'
                    results.append(result)
                    seen_ids.add(result['id'])
        
        # Sort by relevance (semantic results first, then by similarity if available)
        results.sort(key=lambda x: (
            x.get('search_type') != 'semantic',
            -x.get('cosine_similarity', 0)
        ))
        
        return results[:n_results]
        
    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        raise RuntimeError(f"Hybrid search failed: {e}")


def search_by_type(
    collection_name: str,
    node_type: str,
    language: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Search for code chunks by node type (function, class, etc.).
    
    Args:
        collection_name: ChromaDB collection name
        node_type: Type of code node to search for
        language: Optional language filter
        limit: Maximum results to return
        
    Returns:
        List of matching code chunks
        
    Raises:
        ValueError: If collection_name or node_type is empty
        RuntimeError: If search fails
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if not node_type:
        raise ValueError("Node type cannot be empty")
    
    where = {"node_type": node_type}
    if language:
        where["language"] = language
    
    return full_text_search(collection_name, where=where, limit=limit)


__all__ = [
    'full_text_search',
    'hybrid_search',
    'search_by_type',
]
