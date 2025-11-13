"""
Output formatting utilities for CLI search results.

This module provides functions to format and display search results,
file contents, and other CLI output using the centralized logger.
"""

import json
from typing import Any, Dict, List, Optional

from .logger import logger


def format_search_results(results: List[Dict[str, Any]], query: Optional[str] = None, collection: Optional[str] = None) -> None:
    """
    Format and display search results to console using logger.
    
    Args:
        results: List of search result dictionaries
        query: Optional search query string
        collection: Optional collection name
    """
    if not results:
        logger.info("❌ No results found")
        return
    
    # Header
    if query:
        logger.info(f"\n🔍 Search Results: \"{query}\"")
    else:
        logger.info("\n🔍 Search Results")
    
    if collection:
        logger.info(f"Collection: {collection}")
    
    logger.info(f"Found: {len(results)} result(s)\n")
    
    # Results
    for i, result in enumerate(results, 1):
        logger.info("━" * 80)
        
        # Result header with similarity if available
        if 'cosine_similarity' in result:
            logger.info(f"Result {i}/{len(results)} | Similarity: {result['cosine_similarity']:.3f}")
        else:
            logger.info(f"Result {i}/{len(results)}")
        
        logger.info("━" * 80)
        
        # Metadata
        meta = result.get('metadata', {})
        logger.info(f"📄 File: {meta.get('file_path', 'N/A')}")
        
        node_type = meta.get('node_type', 'N/A')
        node_name = meta.get('node_name', 'N/A')
        logger.info(f"🏷️  Type: {node_type} | Symbol: {node_name}")
        
        start_line = meta.get('start_line', 'N/A')
        end_line = meta.get('end_line', 'N/A')
        logger.info(f"📍 Lines: {start_line}-{end_line}\n")
        
        # Content (truncate if too long)
        content = result.get('content', '')
        if len(content) > 500:
            logger.info(content[:500] + "\n... (truncated)")
        else:
            logger.info(content)
        
        logger.info("")


def format_file_content(file_data: Dict[str, Any]) -> None:
    """
    Format and display reconstructed file content using logger.
    
    Args:
        file_data: Dictionary containing file information and chunks
    """
    if not file_data.get('chunks'):
        logger.error(f"❌ File not found: {file_data.get('file_path')}")
        return
    
    logger.info(f"\n📄 File: {file_data['file_path']}")
    logger.info(f"📊 Total chunks: {file_data['total_chunks']}")
    logger.info("━" * 80)
    
    if file_data.get('content'):
        # Full file content available
        logger.info(file_data['content'])
    else:
        # Show individual chunks
        for i, chunk in enumerate(file_data['chunks'], 1):
            logger.info(f"\n--- Chunk {i}/{file_data['total_chunks']} (Lines {chunk['start_line']}-{chunk['metadata'].get('end_line')}) ---")
            logger.info(chunk['content'])


def format_symbol_list(symbols: List[str], title: str = "Symbols") -> None:
    """
    Format and display list of symbols using logger.
    
    Args:
        symbols: List of symbol names
        title: Title for the symbol list
    """
    if not symbols:
        logger.info("❌ No symbols found")
        return
    
    logger.info(f"\n📚 {title}: {len(symbols)} found\n")
    for symbol in symbols:
        logger.info(f"  • {symbol}")
    logger.info("")


def format_file_list(files: List[str]) -> None:
    """
    Format and display list of files using logger.
    
    Args:
        files: List of file paths
    """
    if not files:
        logger.info("❌ No files found")
        return
    
    logger.info(f"\n📁 Files: {len(files)} found\n")
    for file in files:
        logger.info(f"  • {file}")
    logger.info("")


def export_results_json(results: List[Dict[str, Any]], filepath: str) -> None:
    """
    Export search results to JSON file.
    
    Args:
        results: List of search results
        filepath: Path to output JSON file
        
    Raises:
        FileSystemError: If unable to write file
    """
    from .exceptions import FileSystemError
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Results exported to: {filepath}")
    except Exception as e:
        raise FileSystemError(f"Failed to export JSON: {e}", filepath, "write")


__all__ = [
    'export_results_json',
    'export_results_toon',
    'format_file_content',
    'format_file_list',
    'format_search_results',
    'format_symbol_list',
]


def export_results_toon(results: List[Dict[str, Any]], filepath: str) -> None:
    """
    Export search results to TOON format file.
    
    Args:
        results: List of search results
        filepath: Path to output TOON file
        
    Raises:
        FileSystemError: If unable to write file
    """
    from .exceptions import FileSystemError
    from .toon_encoder import toon_encode
    
    try:
        toon_output = toon_encode(results)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(toon_output)
        logger.info(f"✅ Results exported to TOON format: {filepath}")
    except Exception as e:
        raise FileSystemError(f"Failed to export TOON: {e}", filepath, "write")
