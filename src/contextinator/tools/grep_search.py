"""Grep search with TRUE async."""
import re
import asyncio
from typing import Dict, Optional
from collections import defaultdict
from ..utils.logger import logger
from ..config import USE_CHROMA_SERVER

_async_chroma_client = None

async def _get_async_chroma():
    global _async_chroma_client
    if _async_chroma_client is None:
        if USE_CHROMA_SERVER:
            from ..vectorstore.async_chroma import get_async_client
            from ..config import CHROMA_SERVER_URL
            from urllib.parse import urlparse
            parsed = urlparse(CHROMA_SERVER_URL)
            _async_chroma_client = await get_async_client(host=parsed.hostname or "localhost", port=parsed.port or 8000)
        else:
            return None
    return _async_chroma_client

async def grep_search(
    collection_name: str,
    pattern: str,
    max_chunks: int = 100,
    use_regex: bool = False,
    case_sensitive: bool = False,
    whole_word: bool = False,
    context_lines: int = 0,
    language: Optional[str] = None,
    chromadb_dir: Optional[str] = None
) -> Dict:
    """TRUE async grep search."""
    if not collection_name or not pattern:
        raise ValueError("Collection name and pattern required")
    
    regex_pattern = None
    if use_regex:
        flags = 0 if case_sensitive else re.IGNORECASE
        regex_pattern = re.compile(pattern, flags)
    
    where = {"language": language} if language else None
    
    client = await _get_async_chroma()
    from ..config import sanitize_collection_name
    collection = await client.get_collection(sanitize_collection_name(collection_name))
    
    if not use_regex:
        results = await collection.get(
            where_document={"$contains": pattern},
            where=where,
            limit=max_chunks * 2,
            include=['documents', 'metadatas']
        )
    else:
        results = await collection.get(
            where=where,
            limit=max_chunks * 3,
            include=['documents', 'metadatas']
        )
    
    if not results['ids']:
        return {'files': [], 'total_matches': 0, 'total_files': 0, 'pattern': pattern}
    
    file_matches = defaultdict(list)
    total_matches = 0
    
    for doc, meta in zip(results['documents'][:max_chunks], results['metadatas'][:max_chunks]):
        file_path = meta.get('file_path', 'unknown')
        start_line = meta.get('start_line', 1)
        
        for i, line in enumerate(doc.split('\n')):
            matched = False
            
            if use_regex:
                matched = bool(regex_pattern.search(line))
            else:
                search_line = line if case_sensitive else line.lower()
                search_pattern = pattern if case_sensitive else pattern.lower()
                
                if whole_word:
                    word_pattern = r'\b' + re.escape(search_pattern) + r'\b'
                    matched = bool(re.search(word_pattern, search_line, 0 if case_sensitive else re.IGNORECASE))
                else:
                    matched = search_pattern in search_line
            
            if matched:
                file_matches[file_path].append({
                    'line_number': start_line + i,
                    'content': line.strip()
                })
                total_matches += 1
    
    files = [
        {
            'path': path,
            'matches': sorted(matches, key=lambda x: x['line_number']),
            'match_count': len(matches)
        }
        for path, matches in sorted(file_matches.items())
    ]
    
    return {
        'files': files,
        'total_matches': total_matches,
        'total_files': len(files),
        'pattern': pattern
    }

async def find_function_calls(
    collection_name: str,
    function_name: str,
    language: Optional[str] = None,
    chromadb_dir: Optional[str] = None
) -> Dict:
    """Find function calls."""
    if not collection_name or not function_name:
        raise ValueError("Collection name and function name required")
    
    pattern = rf'\b{re.escape(function_name)}\s*\('
    return await grep_search(
        collection_name=collection_name,
        pattern=pattern,
        use_regex=True,
        language=language,
        chromadb_dir=chromadb_dir
    )

__all__ = ['grep_search', 'find_function_calls']
