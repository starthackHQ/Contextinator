"""Semantic search - Natural language code search using embeddings."""
from typing import List, Dict, Any, Optional
from . import SearchTool


def semantic_search(
    collection_name: str,
    query: str,
    n_results: int = 5,
    language: Optional[str] = None,
    file_path: Optional[str] = None,
    node_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for semantically similar code using natural language queries.
    Uses cosine similarity for vector comparison.
    
    Args:
        collection_name: ChromaDB collection name
        query: Natural language query (e.g., "How is authentication handled?")
        n_results: Number of results to return
        language: Optional filter by programming language
        file_path: Optional filter by file path (partial match)
        node_type: Optional filter by node type
    
    Returns:
        List of most relevant chunks with cosine similarity scores
    
    Examples:
        # Find authentication logic
        semantic_search("my-repo", "How is authentication handled?")
        
        # Find error handling in Python
        semantic_search("my-repo", "error handling patterns", language="python")
        
        # Find database logic in specific file
        semantic_search("my-repo", "database connection", file_path="db.py")
    """
    tool = SearchTool(collection_name)
    
    # Build where clause for metadata filters
    where = {}
    if language:
        where["language"] = language
    if file_path:
        where["file_path"] = {"$contains": file_path}
    if node_type:
        where["node_type"] = node_type
    
    # ChromaDB uses cosine similarity by default for query
    results = tool.collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where if where else None,
        include=['documents', 'metadatas', 'distances']
    )
    
    # Format results with cosine similarity scores
    # ChromaDB returns distances, convert to cosine similarity: similarity = 1 - distance
    formatted = []
    for id_, doc, meta, distance in zip(
        results['ids'][0],
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ):
        formatted.append({
            'id': id_,
            'content': doc,
            'metadata': meta,
            'distance': distance,
            'cosine_similarity': 1 - distance
        })
    
    return formatted


def semantic_search_with_context(
    collection_name: str,
    query: str,
    n_results: int = 3,
    **filters
) -> Dict[str, Any]:
    """
    Semantic search with additional context about results.
    
    Args:
        collection_name: ChromaDB collection name
        query: Natural language query
        n_results: Number of results to return
        **filters: Additional metadata filters (language, file_path, node_type)
    
    Returns:
        Dictionary with results and context information
    """
    results = semantic_search(collection_name, query, n_results, **filters)
    
    # Extract context
    files = {r['metadata'].get('file_path') for r in results}
    languages = {r['metadata'].get('language') for r in results}
    node_types = {r['metadata'].get('node_type') for r in results}
    
    return {
        'query': query,
        'total_results': len(results),
        'results': results,
        'context': {
            'files': sorted(files),
            'languages': sorted(languages),
            'node_types': sorted(node_types)
        }
    }
