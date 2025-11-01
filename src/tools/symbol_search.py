"""Symbol search - Find specific functions, classes, or symbols by name."""
from typing import List, Dict, Any, Optional
from . import SearchTool


def symbol_search(
    collection_name: str,
    symbol_name: str,
    node_type: Optional[str] = None,
    file_path: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Find code symbols (functions, classes, methods) by name.
    
    Args:
        collection_name: ChromaDB collection name
        symbol_name: Name of the symbol to find (e.g., "MyClass", "authenticate")
        node_type: Optional filter by node type (e.g., "function_definition", "class_declaration")
        file_path: Optional filter by file path (supports partial match)
        limit: Maximum results to return
    
    Returns:
        List of matching chunks with metadata
    
    Examples:
        # Find class definition
        symbol_search("my-repo", "UserController", node_type="class_declaration")
        
        # Find all functions named "validate"
        symbol_search("my-repo", "validate", node_type="function_definition")
        
        # Find symbol in specific file
        symbol_search("my-repo", "authenticate", file_path="auth.py")
    """
    tool = SearchTool(collection_name)
    
    # Build where clause
    where = {"node_name": symbol_name}
    
    if node_type:
        where["node_type"] = node_type
    
    if file_path:
        where["file_path"] = {"$contains": file_path}
    
    results = tool.collection.get(
        where=where,
        limit=limit,
        include=['documents', 'metadatas']
    )
    
    return tool.format_results(results)


def list_symbols(
    collection_name: str,
    node_type: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 100
) -> List[str]:
    """
    List all unique symbol names in collection.
    
    Args:
        collection_name: ChromaDB collection name
        node_type: Optional filter by node type
        language: Optional filter by language
        limit: Maximum results to fetch
    
    Returns:
        List of unique symbol names
    """
    tool = SearchTool(collection_name)
    
    where = {}
    if node_type:
        where["node_type"] = node_type
    if language:
        where["language"] = language
    
    results = tool.collection.get(
        where=where if where else None,
        limit=limit,
        include=['metadatas']
    )
    
    symbols = {meta.get('node_name') for meta in results['metadatas'] if meta.get('node_name')}
    return sorted(symbols)
