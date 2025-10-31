"""Output formatting utilities for CLI search results."""
import json
from typing import List, Dict, Any, Optional


def format_search_results(results: List[Dict[str, Any]], query: str = None, collection: str = None) -> None:
    """Format and print search results to console."""
    if not results:
        print("❌ No results found")
        return
    
    # Header
    if query:
        print(f"\n🔍 Search Results: \"{query}\"")
    else:
        print(f"\n🔍 Search Results")
    
    if collection:
        print(f"Collection: {collection}")
    
    print(f"Found: {len(results)} result(s)\n")
    
    # Results
    for i, result in enumerate(results, 1):
        print("━" * 80)
        
        # Result header with similarity if available
        if 'cosine_similarity' in result:
            print(f"Result {i}/{len(results)} | Similarity: {result['cosine_similarity']:.3f}")
        else:
            print(f"Result {i}/{len(results)}")
        
        print("━" * 80)
        
        # Metadata
        meta = result.get('metadata', {})
        print(f"📄 File: {meta.get('file_path', 'N/A')}")
        
        node_type = meta.get('node_type', 'N/A')
        node_name = meta.get('node_name', 'N/A')
        print(f"🏷️  Type: {node_type} | Symbol: {node_name}")
        
        start_line = meta.get('start_line', 'N/A')
        end_line = meta.get('end_line', 'N/A')
        print(f"📍 Lines: {start_line}-{end_line}\n")
        
        # Content (truncate if too long)
        content = result.get('content', '')
        if len(content) > 500:
            print(content[:500] + "\n... (truncated)")
        else:
            print(content)
        
        print()


def format_file_content(file_data: Dict[str, Any]) -> None:
    """Format and print reconstructed file content."""
    if not file_data.get('found'):
        print(f"❌ File not found: {file_data.get('file_path')}")
        return
    
    print(f"\n📄 File: {file_data['file_path']}")
    print(f"📊 Total chunks: {file_data['total_chunks']}")
    print("━" * 80)
    
    if file_data.get('content'):
        print(file_data['content'])
    else:
        # Print chunks separately
        for i, chunk in enumerate(file_data.get('chunks', []), 1):
            print(f"\n--- Chunk {i}/{file_data['total_chunks']} (Lines {chunk['start_line']}-{chunk['metadata'].get('end_line')}) ---")
            print(chunk['content'])


def format_symbol_list(symbols: List[str], title: str = "Symbols") -> None:
    """Format and print list of symbols."""
    if not symbols:
        print("❌ No symbols found")
        return
    
    print(f"\n📚 {title}: {len(symbols)} found\n")
    for symbol in symbols:
        print(f"  • {symbol}")
    print()


def format_file_list(files: List[str]) -> None:
    """Format and print list of files."""
    if not files:
        print("❌ No files found")
        return
    
    print(f"\n📁 Files: {len(files)} found\n")
    for file in files:
        print(f"  • {file}")
    print()


def export_json(data: Any, filepath: str) -> None:
    """Export data to JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Results exported to: {filepath}")
    except Exception as e:
        print(f"❌ Failed to export JSON: {e}")
