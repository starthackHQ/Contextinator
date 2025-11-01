"""Regex search - Pattern-based code search in document content."""
from typing import List, Dict, Any, Optional
from . import SearchTool


def regex_search(
    collection_name: str,
    pattern: str,
    language: Optional[str] = None,
    file_path: Optional[str] = None,
    node_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Search for code chunks matching a text pattern.
    
    Args:
        collection_name: ChromaDB collection name
        pattern: Text pattern to search for (substring match)
        language: Optional filter by programming language
        file_path: Optional filter by file path (partial match)
        node_type: Optional filter by node type
        limit: Maximum results to return
    
    Returns:
        List of matching chunks with metadata
    
    Examples:
        # Find all calls to authenticate function
        regex_search("my-repo", "authenticate(")
        
        # Find TODO comments in Python files
        regex_search("my-repo", "TODO", language="python")
        
        # Find imports in specific file
        regex_search("my-repo", "import", file_path="auth.py")
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
    
    results = tool.collection.get(
        where_document={"$contains": pattern},
        where=where if where else None,
        limit=limit,
        include=['documents', 'metadatas']
    )
    
    return tool.format_results(results)


def find_function_calls(
    collection_name: str,
    function_name: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Find all chunks containing calls to a specific function.
    
    Args:
        collection_name: ChromaDB collection name
        function_name: Name of function to find calls for
        limit: Maximum results to return
    
    Returns:
        List of chunks containing function calls
    """
    return regex_search(collection_name, f"{function_name}(", limit=limit)
