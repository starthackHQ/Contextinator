"""Cat file tool - Display complete file contents from chunks."""

from typing import Optional
from . import SearchTool
from ..utils.logger import logger


def cat_file(
    collection_name: str,
    file_path: str,
    chromadb_dir: Optional[str] = None
) -> str:
    """
    Get complete file contents by fetching and joining all chunks.
    
    Args:
        collection_name: ChromaDB collection name
        file_path: Path to file (e.g., "src/main.py")
        chromadb_dir: Optional custom ChromaDB directory
    
    Returns:
        Complete file content as string
    
    Raises:
        ValueError: If file not found
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    logger.debug(f"Cat file: {file_path} in collection {collection_name}")
    
    try:
        tool = SearchTool(collection_name, chromadb_dir=chromadb_dir)
        
        # Get all chunks for this file
        results = tool.collection.get(
            where={"file_path": file_path},
            limit=300,  # Max chunks per file
            include=['documents', 'metadatas']
        )
        
        if not results['ids'] or len(results['ids']) == 0:
            raise ValueError(f"File not found: {file_path}")
        
        # Parse and sort by line number
        chunks = []
        for doc, meta in zip(results['documents'], results['metadatas']):
            chunks.append({
                'content': doc,
                'start_line': meta.get('start_line', 0)
            })
        
        # Sort by start_line
        chunks.sort(key=lambda x: x['start_line'])
        
        # Join content
        content = '\n'.join(chunk['content'] for chunk in chunks)
        
        logger.debug(f"Retrieved {len(chunks)} chunks for {file_path}")
        return content
        
    except Exception as e:
        logger.error(f"Cat file failed: {e}")
        raise RuntimeError(f"Failed to get file contents: {e}")


__all__ = ['cat_file']
