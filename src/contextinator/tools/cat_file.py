"""Cat file with async support."""
import asyncio
from typing import Optional
from . import SearchTool
from ..utils.logger import logger

async def cat_file(
    collection_name: str,
    file_path: str,
    chromadb_dir: Optional[str] = None
) -> str:
    """Get complete file contents."""
    if not collection_name or not file_path:
        raise ValueError("Collection name and file path required")
    
    loop = asyncio.get_event_loop()
    
    def _cat():
        tool = SearchTool(collection_name, chromadb_dir=chromadb_dir)
        
        results = tool.collection.get(
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
    
    return await loop.run_in_executor(None, _cat)

__all__ = ['cat_file']
