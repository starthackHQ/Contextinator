"""
File reading module for Contextinator.

This module provides functionality to read and list files from
the ChromaDB collection with filtering capabilities.
"""

from typing import Any, Dict, List, Optional, Set

from . import SearchTool
from ..utils.logger import logger


def read_file(
    collection_name: str,
    file_path: str,
    node_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Read all chunks from a specific file.
    
    Args:
        collection_name: ChromaDB collection name
        file_path: Path to the file (can be partial)
        node_type: Optional filter by node type
        
    Returns:
        List of chunks from the specified file
        
    Raises:
        ValueError: If collection_name or file_path is empty
        RuntimeError: If search fails
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    logger.debug(f"Reading file '{file_path}' from collection '{collection_name}'")
    
    try:
        tool = SearchTool(collection_name)
        
        where = {"file_path": {"$contains": file_path}}
        if node_type:
            where["node_type"] = node_type
        
        results = tool.collection.get(
            where=where,
            include=['documents', 'metadatas']
        )
        
        formatted = tool.format_results(results)
        
        # Sort by line number if available
        formatted.sort(key=lambda x: x['metadata'].get('start_line', 0))
        
        logger.debug(f"Found {len(formatted)} chunks in file")
        return formatted
        
    except Exception as e:
        logger.error(f"Read file failed: {e}")
        raise RuntimeError(f"Read file failed: {e}")


def list_files(
    collection_name: str,
    language: Optional[str] = None,
    pattern: Optional[str] = None
) -> List[str]:
    """
    List all files in the collection with optional filtering.
    
    Args:
        collection_name: ChromaDB collection name
        language: Optional language filter
        pattern: Optional file path pattern filter
        
    Returns:
        Sorted list of unique file paths
        
    Raises:
        ValueError: If collection_name is empty
        RuntimeError: If listing fails
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    
    logger.debug(f"Listing files in collection '{collection_name}'")
    
    try:
        tool = SearchTool(collection_name)
        
        where = {}
        if language:
            where["language"] = language
        if pattern:
            where["file_path"] = {"$contains": pattern}
        
        results = tool.collection.get(
            where=where if where else None,
            include=['metadatas']
        )
        
        # Extract unique file paths
        files: Set[str] = set()
        for meta in results['metadatas']:
            file_path = meta.get('file_path')
            if file_path:
                files.add(file_path)
        
        sorted_files = sorted(files)
        logger.debug(f"Found {len(sorted_files)} unique files")
        return sorted_files
        
    except Exception as e:
        logger.error(f"List files failed: {e}")
        raise RuntimeError(f"List files failed: {e}")


__all__ = [
    'list_files',
    'read_file',
]
