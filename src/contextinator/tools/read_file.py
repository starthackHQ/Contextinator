"""
File reading module for Contextinator.

This module provides functionality to read and list files from
the ChromaDB collection with filtering capabilities.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from . import SearchTool
from ..utils.logger import logger


def _matches_file_path(stored_path: str, search_path: str) -> bool:
    """
    Check if a stored file path matches the search criteria.
    
    Matches if:
    - Exact match (case-insensitive)
    - Search path is the basename and matches the stored basename
    - Search path is contained at end of stored path (e.g., 'src/file.py' matches 'project/src/file.py')
    
    Args:
        stored_path: The file path stored in metadata
        search_path: The search pattern provided by user
        
    Returns:
        True if paths match, False otherwise
    """
    # Normalize to forward slashes for comparison
    stored_norm = stored_path.replace('\\', '/').lower()
    search_norm = search_path.replace('\\', '/').lower()
    
    # Exact match
    if stored_norm == search_norm:
        return True
    
    # Basename match (e.g., searching "file.py" matches "path/to/file.py")
    stored_basename = Path(stored_norm).name
    search_basename = Path(search_norm).name
    if search_basename and stored_basename == search_basename:
        # Only match if search is just a filename (no path separators)
        if '/' not in search_norm:
            return True
    
    # Suffix match (e.g., searching "src/file.py" matches "project/src/file.py")
    if stored_norm.endswith('/' + search_norm) or stored_norm.endswith(search_norm):
        return True
    
    return False


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

        # Build where clause for filtering
        # Note: get() doesn't support $contains, so we filter in Python
        where = {}
        if node_type:
            where["node_type"] = node_type

        # Get all documents matching node_type filter (if any)
        results = tool.collection.get(
            where=where if where else None,
            include=['documents', 'metadatas']
        )

        # Filter by file_path in Python (since get() doesn't support $contains)
        filtered_results = {
            'ids': [],
            'documents': [],
            'metadatas': []
        }
        
        for id_, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
            # Check if file_path matches using smart matching
            if _matches_file_path(meta.get('file_path', ''), file_path):
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
        
        # Build where clause - get() doesn't support $contains
        where = {}
        if language:
            where["language"] = language
        
        # Get documents with language filter (if any)
        results = tool.collection.get(
            where=where if where else None,
            include=['metadatas']
        )
        
        # Extract unique file paths and filter by pattern using smart matching
        files: Set[str] = set()
        for meta in results['metadatas']:
            file_path_value = meta.get('file_path')
            if file_path_value:
                # Apply pattern filter if specified using smart matching
                if pattern and not _matches_file_path(file_path_value, pattern):
                    continue
                files.add(file_path_value)
        
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
