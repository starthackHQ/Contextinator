"""
Symbol search module for Contextinator.

This module provides functionality to search for specific symbols
like functions, classes, and variables in the codebase.
"""

from typing import Any, Dict, List, Optional, Set

from . import SearchTool
from ..utils.logger import logger


def symbol_search(
    collection_name: str,
    symbol_name: str,
    symbol_type: Optional[str] = None,
    language: Optional[str] = None,
    exact_match: bool = True
) -> List[Dict[str, Any]]:
    """
    Search for specific symbols (functions, classes, variables) by name.
    
    Args:
        collection_name: ChromaDB collection name
        symbol_name: Name of the symbol to search for
        symbol_type: Optional type filter (function, class, etc.)
        language: Optional language filter
        exact_match: Whether to use exact name matching (default: True)
        
    Returns:
        List of chunks containing the symbol
        
    Raises:
        ValueError: If collection_name or symbol_name is empty
        RuntimeError: If search fails
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if not symbol_name:
        raise ValueError("Symbol name cannot be empty")
    
    logger.debug(f"Symbol search: '{symbol_name}' in collection '{collection_name}'")
    
    try:
        tool = SearchTool(collection_name)
        
        # Build where clause
        where = {}
        if language:
            where["language"] = language
        if symbol_type:
            where["node_type"] = symbol_type
        
        # Search by node_name in metadata
        if exact_match:
            where["node_name"] = symbol_name
        else:
            where["node_name"] = {"$contains": symbol_name}
        
        results = tool.collection.get(
            where=where,
            include=['documents', 'metadatas']
        )
        
        formatted = tool.format_results(results)
        
        # Deduplicate by hash to avoid duplicate results
        seen_hashes = set()
        deduplicated = []
        for result in formatted:
            chunk_hash = result['metadata'].get('hash')
            if chunk_hash and chunk_hash not in seen_hashes:
                seen_hashes.add(chunk_hash)
                deduplicated.append(result)
            elif not chunk_hash:  # Keep results without hash
                deduplicated.append(result)
        
        logger.debug(f"Found {len(formatted)} symbol matches, {len(deduplicated)} after deduplication")
        return deduplicated
        
    except Exception as e:
        logger.error(f"Symbol search failed: {e}")
        raise RuntimeError(f"Symbol search failed: {e}")


def list_symbols(
    collection_name: str,
    symbol_type: Optional[str] = None,
    language: Optional[str] = None,
    file_path: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    List all symbols in the collection with optional filtering.
    
    Args:
        collection_name: ChromaDB collection name
        symbol_type: Optional type filter (function, class, etc.)
        language: Optional language filter
        file_path: Optional file path filter
        
    Returns:
        List of symbol information dictionaries
        
    Raises:
        ValueError: If collection_name is empty
        RuntimeError: If listing fails
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    
    logger.debug(f"Listing symbols in collection '{collection_name}'")
    
    try:
        tool = SearchTool(collection_name)
        
        where = {}
        if symbol_type:
            where["node_type"] = symbol_type
        if language:
            where["language"] = language
        if file_path:
            where["file_path"] = {"$contains": file_path}
        
        results = tool.collection.get(
            where=where if where else None,
            include=['metadatas']
        )
        
        # Extract symbol information
        symbols: Set[tuple] = set()
        for meta in results['metadatas']:
            name = meta.get('node_name')  # Changed from 'name' to 'node_name'
            node_type = meta.get('node_type')
            file_path = meta.get('file_path')
            language = meta.get('language')
            
            if name and node_type:
                symbols.add((name, node_type, file_path or '', language or ''))
        
        # Convert to list of dictionaries and sort
        symbol_list = [
            {
                'name': name,
                'type': node_type,
                'file_path': file_path,
                'language': language
            }
            for name, node_type, file_path, language in symbols
        ]
        
        symbol_list.sort(key=lambda x: (x['name'], x['type']))
        
        logger.debug(f"Found {len(symbol_list)} unique symbols")
        return symbol_list
        
    except Exception as e:
        logger.error(f"List symbols failed: {e}")
        raise RuntimeError(f"List symbols failed: {e}")


__all__ = [
    'list_symbols',
    'symbol_search',
]
