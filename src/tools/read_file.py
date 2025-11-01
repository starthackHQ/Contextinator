"""Read file - Reconstruct complete files from chunks."""
from typing import List, Dict, Any, Optional
from . import SearchTool


def read_file(
    collection_name: str,
    file_path: str,
    join_chunks: bool = True
) -> Dict[str, Any]:
    """
    Retrieve and reconstruct a complete file from chunks.
    
    Args:
        collection_name: ChromaDB collection name
        file_path: Full or partial file path to retrieve
        join_chunks: If True, join chunks into single content string
    
    Returns:
        Dictionary with file content and metadata
    
    Examples:
        # Get complete file
        read_file("my-repo", "src/auth.py")
        
        # Get chunks without joining
        read_file("my-repo", "auth.py", join_chunks=False)
    """
    tool = SearchTool(collection_name)
    
    results = tool.collection.get(
        where={"file_path": {"$contains": file_path}},
        include=['documents', 'metadatas']
    )
    
    if not results['ids']:
        return {
            'file_path': file_path,
            'found': False,
            'chunks': [],
            'content': None
        }
    
    # Sort chunks by start_line
    chunks = []
    for id_, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
        chunks.append({
            'id': id_,
            'content': doc,
            'metadata': meta,
            'start_line': meta.get('start_line', 0)
        })
    
    chunks.sort(key=lambda x: x['start_line'])
    
    if join_chunks:
        content = '\n'.join(chunk['content'] for chunk in chunks)
        return {
            'file_path': file_path,
            'found': True,
            'total_chunks': len(chunks),
            'content': content,
            'chunks': chunks
        }
    else:
        return {
            'file_path': file_path,
            'found': True,
            'total_chunks': len(chunks),
            'chunks': chunks
        }


def list_files(
    collection_name: str,
    language: Optional[str] = None,
    path_filter: Optional[str] = None
) -> List[str]:
    """
    List all unique file paths in collection.
    
    Args:
        collection_name: ChromaDB collection name
        language: Optional filter by language
        path_filter: Optional path substring filter
    
    Returns:
        Sorted list of unique file paths
    """
    tool = SearchTool(collection_name)
    
    where = {}
    if language:
        where["language"] = language
    if path_filter:
        where["file_path"] = {"$contains": path_filter}
    
    results = tool.collection.get(
        where=where if where else None,
        include=['metadatas']
    )
    
    files = {meta.get('file_path') for meta in results['metadatas'] if meta.get('file_path')}
    return sorted(files)
