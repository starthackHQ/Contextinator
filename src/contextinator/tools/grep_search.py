"""Advanced grep search tool using ChromaDB $contains operator."""

from typing import Dict, List, Optional
from collections import defaultdict
from . import SearchTool
from ..utils.logger import logger


def grep_search(
    collection_name: str,
    pattern: str,
    max_chunks: int = 50,
    chromadb_dir: Optional[str] = None
) -> Dict:
    """
    Advanced grep search using ChromaDB $contains operator.
    Fast and accurate pattern matching across all files.
    
    Args:
        collection_name: ChromaDB collection name
        pattern: Text pattern to search for
        max_chunks: Maximum chunks to retrieve (default: 50)
        chromadb_dir: Optional custom ChromaDB directory
    
    Returns:
        Dict with structure:
        {
            "files": [
                {
                    "path": "src/main.py",
                    "matches": [
                        {"line_number": 10, "content": "matching line"},
                        ...
                    ]
                },
                ...
            ],
            "total_matches": 15,
            "total_files": 3
        }
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if not pattern:
        raise ValueError("Pattern cannot be empty")
    
    logger.debug(f"Grep search: '{pattern}' in collection {collection_name}")
    
    try:
        tool = SearchTool(collection_name, chromadb_dir=chromadb_dir)
        
        # Use $contains operator for fast search
        results = tool.collection.get(
            where_document={"$contains": pattern},
            limit=max_chunks,
            include=['documents', 'metadatas']
        )
        
        if not results['ids']:
            return {"files": [], "total_matches": 0, "total_files": 0}
        
        # Group matches by file
        file_matches = defaultdict(list)
        total_matches = 0
        
        for doc, meta in zip(results['documents'], results['metadatas']):
            file_path = meta.get('file_path', 'unknown')
            start_line = meta.get('start_line', 1)
            
            # Find matching lines in chunk
            lines = doc.split('\n')
            for i, line in enumerate(lines):
                if pattern in line:
                    line_number = start_line + i
                    file_matches[file_path].append({
                        'line_number': line_number,
                        'content': line.strip()
                    })
                    total_matches += 1
        
        # Format results
        files = []
        for path in sorted(file_matches.keys()):
            matches = sorted(file_matches[path], key=lambda x: x['line_number'])
            files.append({
                'path': path,
                'matches': matches
            })
        
        result = {
            'files': files,
            'total_matches': total_matches,
            'total_files': len(files)
        }
        
        logger.debug(f"Found {total_matches} matches in {len(files)} files")
        return result
        
    except Exception as e:
        logger.error(f"Grep search failed: {e}")
        raise RuntimeError(f"Grep search failed: {e}")


__all__ = ['grep_search']
