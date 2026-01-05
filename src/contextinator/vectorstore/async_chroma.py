"""Async ChromaDB client wrapper with singleton caching."""
import chromadb

_client_cache = {}

async def get_async_client(host: str = "localhost", port: int = 8000):
    """Get cached ChromaDB async client (singleton per host:port)."""
    key = f"{host}:{port}"
    if key not in _client_cache:
        _client_cache[key] = await chromadb.AsyncHttpClient(host=host, port=port)
    return _client_cache[key]


__all__ = ['get_async_client']
