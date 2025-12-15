"""Symbol search with TRUE async."""
from typing import Any, Dict, List, Optional
from ..utils.logger import logger
from ..config import USE_CHROMA_SERVER
import asyncio

_async_chroma_client = None

async def _get_async_chroma():
    """Get async ChromaDB client."""
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

async def symbol_search(
    collection_name: str,
    symbol_name: str,
    symbol_type: Optional[str] = None,
    language: Optional[str] = None,
    exact_match: bool = True,
    chromadb_dir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """TRUE async symbol search."""
    if not collection_name or not symbol_name:
        raise ValueError("Collection name and symbol name required")
    
    where = {}
    if language:
        where["language"] = language
    if symbol_type:
        where["node_type"] = symbol_type
    if exact_match:
        where["node_name"] = symbol_name
    
    client = await _get_async_chroma()
    from ..config import sanitize_collection_name
    collection = await client.get_collection(sanitize_collection_name(collection_name))
    results = await collection.get(where=where if where else None, include=['documents', 'metadatas'])
    
    if not exact_match:
        filtered = {'ids': [], 'documents': [], 'metadatas': []}
        for id_, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
            if symbol_name.lower() in meta.get('node_name', '').lower():
                filtered['ids'].append(id_)
                filtered['documents'].append(doc)
                filtered['metadatas'].append(meta)
        results = filtered
    
    seen = set()
    deduped = []
    for id_, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
        h = meta.get('hash')
        if not h or h not in seen:
            if h:
                seen.add(h)
            deduped.append({'id': id_, 'content': doc, 'metadata': meta})
    
    return deduped

async def list_symbols(
    collection_name: str,
    symbol_type: Optional[str] = None,
    language: Optional[str] = None,
    file_path: Optional[str] = None
) -> List[Dict[str, str]]:
    """TRUE async list symbols."""
    if not collection_name:
        raise ValueError("Collection name required")
    
    where = {}
    if symbol_type:
        where["node_type"] = symbol_type
    if language:
        where["language"] = language
    
    client = await _get_async_chroma()
    from ..config import sanitize_collection_name
    collection = await client.get_collection(sanitize_collection_name(collection_name))
    results = await collection.get(where=where if where else None, include=['metadatas'])
    
    symbols = set()
    for meta in results['metadatas']:
        if file_path and file_path not in meta.get('file_path', ''):
            continue
        name = meta.get('node_name')
        node_type = meta.get('node_type')
        if name and node_type:
            symbols.add((name, node_type, meta.get('file_path', ''), meta.get('language', '')))
    
    return sorted([
        {'name': n, 'type': t, 'file_path': f, 'language': l}
        for n, t, f, l in symbols
    ], key=lambda x: (x['name'], x['type']))

__all__ = ['symbol_search', 'list_symbols']
