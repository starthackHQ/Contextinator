"""Cat file with TRUE async."""

import asyncio
import hashlib
from typing import Dict, List, Optional
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
            _async_chroma_client = await get_async_client(
                host=parsed.hostname or "localhost", port=parsed.port or 8000
            )
        else:
            return None
    return _async_chroma_client


async def cat_file(
    collection_name: str, file_path: str, chromadb_dir: Optional[str] = None
) -> str:
    """TRUE async cat file."""
    if not collection_name or not file_path:
        raise ValueError("Collection name and file path required")

    if file_path.startswith("/"):
        file_path = file_path[1:]

    client = await _get_async_chroma()
    from ..config import sanitize_collection_name

    collection = await client.get_collection(sanitize_collection_name(collection_name))

    results = await collection.get(
        where={"file_path": file_path}, include=["documents", "metadatas"]
    )

    if not results["ids"]:
        raise ValueError(f"File not found: {file_path}")

    logger.debug(f"Found {len(results['ids'])} chunks for file: {file_path}")

    # Parse and enrich chunk metadata
    chunks = []
    for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
        chunk = {
            "content": doc,
            "start_line": meta.get("start_line", 0),
            "end_line": meta.get("end_line", 0), 
            "split_index": meta.get("split_index", 0),
            "parent_id": meta.get("parent_id"),
            "is_split": meta.get("is_split", False),
            "original_id": meta.get("original_id"),
            "node_type": meta.get("node_type", "unknown"),
            "chunk_id": results["ids"][i],
        }
        chunks.append(chunk)
        
    # Sort chunks by start_line first, then by split_index, then by end_line
    chunks.sort(key=lambda x: (x["start_line"], x["split_index"], x["end_line"]))
    
    logger.debug(f"Chunk details: {[(c['start_line'], c['end_line'], c['is_split'], c['split_index'], len(c['content'])) for c in chunks]}")

    # Reconstruct file
    return _reconstruct_file(chunks)


def _reconstruct_file(chunks: List[Dict]) -> str:
    """Deduplicate and concatenate chunks, removing nested duplicates."""
    if not chunks:
        return ""
    
    # Sort by start_line, then by length (longer first)
    chunks.sort(key=lambda x: (int(x.get('start_line', 0)), -int(x.get('end_line', 0))))
    
    # Remove chunks that are completely contained in other chunks
    unique = []
    for c in chunks:
        c_start = int(c.get('start_line', 0))
        c_end = int(c.get('end_line', 0))
        
        # Check if this chunk is contained in any already-kept chunk
        is_contained = False
        for kept in unique:
            k_start = int(kept.get('start_line', 0))
            k_end = int(kept.get('end_line', 0))
            
            # If c is completely inside kept, skip it
            if k_start <= c_start and c_end <= k_end and (k_start != c_start or k_end != c_end):
                is_contained = True
                break
        
        if not is_contained:
            unique.append(c)
    
    # Concatenate with double newline between chunks
    return '\n\n'.join(c.get('content', '').strip() for c in unique if c.get('content', '').strip())


__all__ = ["cat_file"]
