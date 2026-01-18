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

    chunks = sorted(
        [
            {
                "content": doc,
                "start_line": meta.get("start_line", 0),
                "end_line": meta.get("end_line", 0),
                "split_index": meta.get("split_index", 0),
                "parent_id": meta.get("parent_id"),
            }
            for doc, meta in zip(results["documents"], results["metadatas"])
        ],
        key=lambda x: (x["start_line"], x["split_index"]),
    )

    # Deduplicate overlapping chunks and filter out nested children
    seen_ranges = set()
    unique_chunks = []
    for chunk in chunks:
        range_key = (chunk["start_line"], chunk["end_line"])
        # Skip if same range already seen OR if this chunk is nested inside another
        if range_key in seen_ranges:
            continue
        # Check if this chunk is contained within any already added chunk
        is_nested = any(
            uc["start_line"] <= chunk["start_line"] and uc["end_line"] >= chunk["end_line"]
            and (uc["start_line"], uc["end_line"]) != range_key
            for uc in unique_chunks
        )
        if not is_nested:
            seen_ranges.add(range_key)
            unique_chunks.append(chunk)

    return "\n".join(c["content"] for c in unique_chunks)


__all__ = ["cat_file"]
