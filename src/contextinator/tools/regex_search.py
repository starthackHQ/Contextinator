"""
Regex search module for Contextinator.

This module provides regular expression-based search functionality
for finding code patterns and specific constructs.
"""

import re
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


def regex_search(
    collection_name: str,
    pattern: str,
    flags: int = re.IGNORECASE,
    language: Optional[str] = None,
    file_path: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Search code using regular expressions.
    
    Args:
        collection_name: ChromaDB collection name
        pattern: Regular expression pattern
        flags: Regex flags (default: re.IGNORECASE)
        language: Optional language filter
        file_path: Optional file path filter
        limit: Maximum results to return
        
    Returns:
        List of matching chunks with regex match details
        
    Raises:
        ValueError: If collection_name or pattern is empty
        re.error: If regex pattern is invalid
        RuntimeError: If search fails
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if not pattern:
        raise ValueError("Pattern cannot be empty")
    
    try:
        compiled_pattern = re.compile(pattern, flags)
    except re.error as e:
        raise re.error(f"Invalid regex pattern: {e}")
    
    logger.debug(f"Regex search: '{pattern}' in collection '{collection_name}'")
    
    try:
        tool = SearchTool(collection_name)
        
        # Build where clause (get() doesn't support $contains)
        where = {}
        if language:
            where["language"] = language
        # file_path filtering will be done in Python since get() doesn't support $contains
        
        # Get all matching documents
        results = tool.collection.get(
            where=where if where else None,
            include=['documents', 'metadatas']
        )
        
        # Filter by file_path (if specified) and regex pattern, apply limit
        matches = []
        for id_, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
            # Stop if we've reached the limit
            if len(matches) >= limit:
                break
            
            # Apply file_path filter if specified using smart matching
            if file_path and not _matches_file_path(meta.get('file_path', ''), file_path):
                continue
                
            regex_matches = list(compiled_pattern.finditer(doc))
            if regex_matches:
                matches.append({
                    'id': id_,
                    'content': doc,
                    'metadata': meta,
                    'matches': [
                        {
                            'match': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'groups': match.groups()
                        }
                        for match in regex_matches
                    ],
                    'match_count': len(regex_matches)
                })
        
        logger.debug(f"Found {len(matches)} regex matches")
        return matches
        
    except Exception as e:
        logger.error(f"Regex search failed: {e}")
        raise RuntimeError(f"Regex search failed: {e}")


def find_function_calls(
    collection_name: str,
    function_name: str,
    language: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Find function calls using language-specific patterns.
    
    Args:
        collection_name: ChromaDB collection name
        function_name: Name of function to find calls for
        language: Programming language for pattern optimization
        
    Returns:
        List of chunks containing function calls
        
    Raises:
        ValueError: If collection_name or function_name is empty
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if not function_name:
        raise ValueError("Function name cannot be empty")
    
    # Language-specific patterns for function calls
    patterns = {
        'python': rf'\b{re.escape(function_name)}\s*\(',
        'javascript': rf'\b{re.escape(function_name)}\s*\(',
        'typescript': rf'\b{re.escape(function_name)}\s*\(',
        'java': rf'\b{re.escape(function_name)}\s*\(',
        'go': rf'\b{re.escape(function_name)}\s*\(',
        'rust': rf'\b{re.escape(function_name)}\s*\(',
    }
    
    pattern = patterns.get(language, rf'\b{re.escape(function_name)}\s*\(')
    
    return regex_search(
        collection_name=collection_name,
        pattern=pattern,
        language=language
    )


__all__ = [
    'find_function_calls',
    'regex_search',
]
