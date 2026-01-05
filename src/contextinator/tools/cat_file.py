"""Cat file with TRUE async."""
import asyncio
from typing import Optional
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

async def cat_file(
    collection_name: str,
    file_path: str,
    chromadb_dir: Optional[str] = None
) -> str:
    """TRUE async cat file."""
    if not collection_name or not file_path:
        raise ValueError("Collection name and file path required")
    
    client = await _get_async_chroma()
    from ..config import sanitize_collection_name
    collection = await client.get_collection(sanitize_collection_name(collection_name))
    
    results = await collection.get(
        where={"file_path": file_path},
        limit=300,
        include=['documents', 'metadatas']
    )
    
    if not results['ids']:
        raise ValueError(f"File not found: {file_path}")
    
    chunks = sorted([
        {'content': doc, 'start_line': meta.get('start_line', 0)}
        for doc, meta in zip(results['documents'], results['metadatas'])
    ], key=lambda x: x['start_line'])
    
    return '\n'.join(c['content'] for c in chunks)

__all__ = ['cat_file']
