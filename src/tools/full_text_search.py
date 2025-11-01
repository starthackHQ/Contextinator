"""Full text search - Advanced multi-criteria search combining filters."""
from typing import List, Dict, Any, Optional
from . import SearchTool


def full_text_search(
    collection_name: str,
    text_pattern: Optional[str] = None,
    where: Optional[Dict[str, Any]] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Advanced search with flexible metadata filtering.
    
    Args:
        collection_name: ChromaDB collection name
        text_pattern: Optional text pattern to search in content
        where: ChromaDB where clause for metadata filtering
        limit: Maximum results to return
    
    Returns:
        List of matching chunks
    
    Examples:
        # Find all imports in auth.ts
        full_text_search("my-repo", 
            text_pattern="import",
            where={"file_path": {"$contains": "auth.ts"}})
        
        # Get all Python functions in utils directory
        full_text_search("my-repo",
            where={"$and": [
                {"language": "python"},
                {"node_type": "function_definition"},
                {"file_path": {"$contains": "utils/"}}
            ]})
    """
    tool = SearchTool(collection_name)
    
    if text_pattern:
        results = tool.collection.get(
            where_document={"$contains": text_pattern},
            where=where,
            limit=limit,
            include=['documents', 'metadatas']
        )
    else:
        results = tool.collection.get(
            where=where,
            limit=limit,
            include=['documents', 'metadatas']
        )
    
    return tool.format_results(results)


def hybrid_search(
    collection_name: str,
    semantic_query: str,
    metadata_filters: Optional[Dict[str, Any]] = None,
    n_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Hybrid search combining semantic similarity with metadata filtering.
    
    Args:
        collection_name: ChromaDB collection name
        semantic_query: Natural language query for semantic search
        metadata_filters: Metadata filters to apply
        n_results: Number of results to return
    
    Returns:
        List of semantically similar chunks matching filters
    
    Examples:
        # Find auth logic in Python files
        hybrid_search("my-repo",
            semantic_query="authentication and authorization",
            metadata_filters={"language": "python"})
    """
    tool = SearchTool(collection_name)
    
    results = tool.collection.query(
        query_texts=[semantic_query],
        n_results=n_results,
        where=metadata_filters,
        include=['documents', 'metadatas', 'distances']
    )
    
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


def search_by_type(
    collection_name: str,
    node_type: str,
    language: Optional[str] = None,
    file_pattern: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Search for all chunks of a specific node type.
    
    Args:
        collection_name: ChromaDB collection name
        node_type: Node type to search for (e.g., "function_definition", "class_declaration")
        language: Optional language filter
        file_pattern: Optional file path pattern
        limit: Maximum results
    
    Returns:
        List of chunks matching the node type
    
    Examples:
        # Get all Python classes
        search_by_type("my-repo", "class_definition", language="python")
        
        # Get all functions in auth files
        search_by_type("my-repo", "function_definition", file_pattern="auth")
    """
    where = {"node_type": node_type}
    
    if language:
        where["language"] = language
    if file_pattern:
        where["file_path"] = {"$contains": file_pattern}
    
    return full_text_search(collection_name, where=where, limit=limit)
