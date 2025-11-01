#!/usr/bin/env python3
"""Example usage of Contextinator search tools."""

from src.tools import (
    symbol_search,
    list_symbols,
    regex_search,
    find_function_calls,
    read_file,
    list_files,
    semantic_search,
    semantic_search_with_context,
    full_text_search,
    hybrid_search,
    search_by_type
)


def example_symbol_search():
    """Example: Find specific symbols by name."""
    print("\n" + "="*60)
    print("1. SYMBOL SEARCH - Find specific functions/classes")
    print("="*60)
    
    # Find a class
    results = symbol_search("Market-FusionX", "UserController", node_type="class_declaration")
    print(f"Found {len(results)} results for 'UserController' class")
    
    # List all symbols
    symbols = list_symbols("Market-FusionX", node_type="function_definition", limit=20)
    print(f"Found {len(symbols)} unique function names")
    print(f"Sample: {symbols[:5]}")


def example_regex_search():
    """Example: Pattern-based search."""
    print("\n" + "="*60)
    print("2. REGEX SEARCH - Find code patterns")
    print("="*60)
    
    # Find function calls
    results = find_function_calls("Market-FusionX", "authenticate")
    print(f"Found {len(results)} calls to 'authenticate()'")
    
    # Find TODO comments
    results = regex_search("Market-FusionX", "TODO", limit=10)
    print(f"Found {len(results)} TODO comments")


def example_read_file():
    """Example: Reconstruct files."""
    print("\n" + "="*60)
    print("3. READ FILE - Reconstruct complete files")
    print("="*60)
    
    # List all files
    files = list_files("Market-FusionX", language="python")
    print(f"Found {len(files)} Python files")
    
    if files:
        # Read first file
        file_data = read_file("Market-FusionX", files[0])
        print(f"\nFile: {file_data['file_path']}")
        print(f"Chunks: {file_data['total_chunks']}")
        print(f"Content length: {len(file_data['content'])} chars")


def example_semantic_search():
    """Example: Natural language search."""
    print("\n" + "="*60)
    print("4. SEMANTIC SEARCH - Natural language queries")
    print("="*60)
    
    # Basic semantic search
    results = semantic_search("Market-FusionX", "How is authentication handled?", n_results=3)
    print(f"Found {len(results)} results for 'authentication' query")
    
    for i, result in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"    Similarity: {result['cosine_similarity']:.3f}")
        print(f"    File: {result['metadata'].get('file_path', 'N/A')}")
        print(f"    Type: {result['metadata'].get('node_type', 'N/A')}")
    
    # Search with context
    result = semantic_search_with_context("Market-FusionX", "database connection", n_results=3)
    print(f"\nContext: {result['context']}")


def example_full_text_search():
    """Example: Advanced multi-criteria search."""
    print("\n" + "="*60)
    print("5. FULL TEXT SEARCH - Advanced queries")
    print("="*60)
    
    # Search by type
    results = search_by_type("Market-FusionX", "function_definition", language="python", limit=10)
    print(f"Found {len(results)} Python functions")
    
    # Hybrid search
    results = hybrid_search(
        "Market-FusionX",
        semantic_query="error handling",
        metadata_filters={"language": "python"},
        n_results=5
    )
    print(f"Found {len(results)} results for hybrid search")


def main():
    """Run all examples."""
    print("\n🔍 CONTEXTINATOR SEARCH TOOLS - EXAMPLES")
    print("="*60)
    print("Collection: Market-FusionX")
    
    try:
        example_symbol_search()
        example_regex_search()
        example_read_file()
        example_semantic_search()
        example_full_text_search()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure ChromaDB server is running and collection exists.")


if __name__ == "__main__":
    main()
