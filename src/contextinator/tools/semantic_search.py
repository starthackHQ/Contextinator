"""Semantic search with TRUE async (no thread pool)."""
from typing import Any, Dict, List, Optional
from ..utils.logger import logger
from ..config import USE_CHROMA_SERVER

_async_embedding_service = None
_async_chroma_client = None

def _get_async_embedding_service():
    global _async_embedding_service
    if _async_embedding_service is None:
        from openai import AsyncOpenAI
        from ..config import OPENAI_API_KEY
        _async_embedding_service = AsyncOpenAI(api_key=OPENAI_API_KEY)
    return _async_embedding_service

async def _get_async_chroma_client():
    """Get async ChromaDB client (official AsyncHttpClient)."""
    global _async_chroma_client
    if _async_chroma_client is None:
        if USE_CHROMA_SERVER:
            from ..vectorstore.async_chroma import get_async_client
            from ..config import CHROMA_SERVER_URL
            from urllib.parse import urlparse
            parsed = urlparse(CHROMA_SERVER_URL)
            _async_chroma_client = await get_async_client(
                host=parsed.hostname or "localhost",
                port=parsed.port or 8000
            )
        else:
            return None  # Signal to use fallback
    return _async_chroma_client

async def semantic_search(
    collection_name: str,
    query: str,
    n_results: int = 5,
    language: Optional[str] = None,
    file_path: Optional[str] = None,
    node_type: Optional[str] = None,
    include_parents: bool = False,
    chromadb_dir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """TRUE async semantic search (no thread pool!)."""
    from ..utils.exceptions import ValidationError
    import asyncio
    
    if not collection_name or not query or n_results <= 0:
        raise ValidationError("Invalid parameters", "params", "valid values")
    
    # Get embedding async (TRUE async - no threads!)
    client = _get_async_embedding_service()
    enriched_query = f"Language: {language}\n\n{query}" if language else query
    
    response = await client.embeddings.create(
        model="text-embedding-3-large",
        input=enriched_query
    )
    query_embedding = response.data[0].embedding
    
    # Build filters
    where = {}
    if language:
        where["language"] = language
    if file_path:
        where["file_path"] = {"$contains": file_path}
    if node_type:
        where["node_type"] = node_type
    if not include_parents:
        where["is_parent"] = False
    
    # Try true async ChromaDB first
    chroma_client = await _get_async_chroma_client()
    
    if chroma_client:
        # TRUE ASYNC - Official ChromaDB AsyncHttpClient
        try:
            from ..config import sanitize_collection_name
            safe_name = sanitize_collection_name(collection_name)
            collection = await chroma_client.get_collection(safe_name)
            
            results = await collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where if where else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            if not results or not results.get('ids') or not results['ids'][0]:
                return []
            
            return [
                {
                    'id': id_,
                    'content': doc,
                    'metadata': meta,
                    'distance': dist,
                    'cosine_similarity': 1 - dist
                }
                for id_, doc, meta, dist in zip(
                    results['ids'][0],
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )
            ]
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            raise

async def semantic_search_with_context(
    collection_name: str,
    query: str,
    n_results: int = 3,
    **filters: Any
) -> Dict[str, Any]:
    """Semantic search with context."""
    results = await semantic_search(collection_name, query, n_results, **filters)
    
    files = sorted({r['metadata'].get('file_path') for r in results if r['metadata'].get('file_path')})
    languages = sorted({r['metadata'].get('language') for r in results if r['metadata'].get('language')})
    node_types = sorted({r['metadata'].get('node_type') for r in results if r['metadata'].get('node_type')})
    
    return {
        'query': query,
        'total_results': len(results),
        'results': results,
        'context': {'files': files, 'languages': languages, 'node_types': node_types},
        'filters_applied': filters
    }

__all__ = ['semantic_search', 'semantic_search_with_context']
