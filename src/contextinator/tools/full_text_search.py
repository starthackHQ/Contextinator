"""
Full text search module for Contextinator.

This module provides advanced multi-criteria search functionality combining
text patterns with metadata filters for precise code discovery.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from . import SearchTool
from ..utils.logger import logger


def _matches_file_path(stored_path: str, search_path: str) -> bool:
    """
    Check if a stored file path matches the search criteria.
    
    Matches if:
    - Exact match (case-insensitive)
    - Search path is the basename and matches the stored basename
    - Search path is contained at end of stored path
    
    Args:
        stored_path: The file path stored in metadata
        search_path: The search pattern provided by user
        
    Returns:
        True if paths match, False otherwise
    """
    stored_norm = stored_path.replace('\\', '/').lower()
    search_norm = search_path.replace('\\', '/').lower()
    
    if stored_norm == search_norm:
        return True
    
    stored_basename = Path(stored_norm).name
    search_basename = Path(search_norm).name
    if search_basename and stored_basename == search_basename:
        if '/' not in search_norm:
            return True
    
    if stored_norm.endswith('/' + search_norm) or stored_norm.endswith(search_norm):
        return True
    
    return False


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
        ValidationError: If collection_name is empty or limit is non-positive
        SearchError: If search fails
    
    Examples:
        >>> # Find all imports in auth.ts
        >>> full_text_search("my-repo", 
        ...     text_pattern="import",
        ...     where={"file_path": {"$contains": "auth.ts"}})
        
        >>> # Get all Python functions in utils directory
        >>> full_text_search("my-repo",
        ...     where={"language": "python", "node_type": "function"})
    """
    from ..utils.exceptions import ValidationError, SearchError
    
    if not collection_name:
        raise ValidationError("Collection name cannot be empty", "collection_name", "non-empty string")
    if limit <= 0:
        raise ValidationError("Limit must be positive", "limit", "positive integer")
    
    logger.debug(f"Full text search in collection '{collection_name}'")
    
    try:
        # Handle missing collection gracefully
        try:
            tool = SearchTool(collection_name)
        except ValidationError as e:
            # Collection doesn't exist
            logger.warning(f"Collection '{collection_name}' not found: {e}")
            return []
        
        # Build where clause for metadata filtering (get() doesn't support $contains)
        where_for_get = {}
        if where:
            # Extract only supported operators for get()
            for key, value in where.items():
                # Skip $contains in where clause, we'll filter in Python
                if isinstance(value, dict) and '$contains' in value:
                    continue
                where_for_get[key] = value
        
        # Get all documents matching metadata filters
        results = tool.collection.get(
            where=where_for_get if where_for_get else None,
            include=['documents', 'metadatas']
        )
        
        # Apply text_pattern and $contains filters in Python
        filtered_results = {
            'ids': [],
            'documents': [],
            'metadatas': []
        }
        
        for id_, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
            # Apply text pattern filter
            if text_pattern and text_pattern.lower() not in doc.lower():
                continue
            
            # Apply $contains filters from where clause using smart matching
            if where:
                skip = False
                for key, value in where.items():
                    if isinstance(value, dict) and '$contains' in value:
                        # Use smart matching for file_path
                        if key == 'file_path':
                            if not _matches_file_path(meta.get(key, ''), value['$contains']):
                                skip = True
                                break
                        # Simple substring match for other fields
                        elif value['$contains'] not in meta.get(key, ''):
                            skip = True
                            break
                if skip:
                    continue
            
            filtered_results['ids'].append(id_)
            filtered_results['documents'].append(doc)
            filtered_results['metadatas'].append(meta)
            
            # Apply limit
            if len(filtered_results['ids']) >= limit:
                break
        
        formatted = tool.format_results(filtered_results)
        logger.debug(f"Found {len(formatted)} matches")
        return formatted
        
    except (ValidationError, SearchError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logger.error(f"Full text search failed: {e}")
        raise SearchError(f"Full text search failed: {e}", text_pattern or "metadata_filter", "full_text")


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
            
            # Extract individual filters from where dict for semantic_search
            kwargs = {}
            if where:
                if 'language' in where:
                    kwargs['language'] = where['language']
                if 'file_path' in where:
                    # Handle both string and dict formats
                    file_path_filter = where['file_path']
                    if isinstance(file_path_filter, dict) and '$contains' in file_path_filter:
                        kwargs['file_path'] = file_path_filter['$contains']
                    else:
                        kwargs['file_path'] = file_path_filter
                if 'node_type' in where:
                    kwargs['node_type'] = where['node_type']
            
            semantic_results = semantic_search(
                collection_name, semantic_query, n_results, **kwargs
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
