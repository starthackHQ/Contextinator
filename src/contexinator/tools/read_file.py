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
    node_type: Optional[str] = None,
    join_chunks: bool = True,
) -> Dict[str, Any]:
    """
    Read and (optionally) reconstruct a file from its chunks in ChromaDB.

    Args:
        collection_name: ChromaDB collection name
        file_path: Path to the file (can be partial)
        node_type: Optional filter by node type
        join_chunks: If True, return a `content` string with all chunks joined

    Returns:
        A dictionary with keys:
          - file_path: the requested file_path
          - total_chunks: number of chunks found
          - chunks: list of chunk dicts ({'id','content','metadata','start_line'})
          - content: (optional) the reconstructed file content when join_chunks=True

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

        # Build where clause - ChromaDB get() doesn't support $contains
        # So we fetch all and filter in Python, or use exact match if possible
        where = None
        if node_type:
            where = {"node_type": node_type}

        # Get all documents (or filtered by node_type if specified)
        results = tool.collection.get(
            where=where,
            include=['documents', 'metadatas']
        )

        # Filter by file_path in Python (since ChromaDB get doesn't support $contains)
        filtered_results = {
            'ids': [],
            'documents': [],
            'metadatas': []
        }
        
        for id_, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
            # Check if file_path contains the search term
            if file_path in meta.get('file_path', ''):
                filtered_results['ids'].append(id_)
                filtered_results['documents'].append(doc)
                filtered_results['metadatas'].append(meta)

        formatted = tool.format_results(filtered_results)

        # Ensure metadata present and sort by start_line
        formatted.sort(key=lambda x: x.get('metadata', {}).get('start_line', 0))

        # Add a top-level start_line field on each chunk for convenience
        for item in formatted:
            item['start_line'] = item.get('metadata', {}).get('start_line')

        file_data: Dict[str, Any] = {
            'file_path': file_path,
            'total_chunks': len(formatted),
            'chunks': formatted,
        }

        # Optionally join chunks into a single content string
        if join_chunks and formatted:
            # Join chunk contents in order using newline; preserve chunk order already sorted above
            joined = '\n'.join([c.get('content', '') for c in formatted])
            file_data['content'] = joined

        logger.debug(f"Found {len(formatted)} chunks in file")
        return file_data

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
        # Note: pattern filtering will be done in Python since get() doesn't support $contains
        
        results = tool.collection.get(
            where=where if where else None,
            include=['metadatas']
        )
        
        # Extract unique file paths
        files: Set[str] = set()
        for meta in results['metadatas']:
            file_path = meta.get('file_path')
            if file_path:
                # Apply pattern filter if specified
                if pattern and pattern not in file_path:
                    continue
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
