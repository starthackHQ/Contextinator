"""Advanced grep search tool with regex support."""

import re
from typing import Dict, List, Optional
from collections import defaultdict
from . import SearchTool
from ..utils.logger import logger


def grep_search(
    collection_name: str,
    pattern: str,
    max_chunks: int = 100,
    use_regex: bool = False,
    case_sensitive: bool = False,
    whole_word: bool = False,
    context_lines: int = 0,
    language: Optional[str] = None,
    chromadb_dir: Optional[str] = None
) -> Dict:
    """
    Advanced grep search with optional regex support.
    Fast and accurate pattern matching across all files.
    
    Args:
        collection_name: ChromaDB collection name
        pattern: Text pattern or regex to search for
        max_chunks: Maximum chunks to retrieve (default: 100)
        use_regex: Enable regex pattern matching (default: False)
        case_sensitive: Case-sensitive matching (default: False)
        whole_word: Match whole words only (default: False, ignored if use_regex=True)
        context_lines: Number of context lines before/after match (default: 0)
        language: Filter by programming language (optional)
        chromadb_dir: Optional custom ChromaDB directory
    
    Returns:
        Dict with structure:
        {
            "files": [
                {
                    "path": "src/main.py",
                    "matches": [
                        {
                            "line_number": 10,
                            "content": "matching line",
                            "context_before": ["line 8", "line 9"],
                            "context_after": ["line 11", "line 12"]
                        }
                    ],
                    "match_count": 5
                }
            ],
            "total_matches": 15,
            "total_files": 3,
            "pattern": "search_term"
        }
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if not pattern:
        raise ValueError("Pattern cannot be empty")
    
    logger.debug(f"Grep search: '{pattern}' (regex={use_regex}, case_sensitive={case_sensitive}) in collection {collection_name}")
    
    try:
        tool = SearchTool(collection_name, chromadb_dir=chromadb_dir)
        
        # Compile regex if needed
        regex_pattern = None
        if use_regex:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                regex_pattern = re.compile(pattern, flags)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        
        # Build where clause for language filter
        where = {}
        if language:
            where["language"] = language
        
        # Use $contains for fast initial filtering (only for non-regex simple text)
        if not use_regex:
            results = tool.collection.get(
                where_document={"$contains": pattern},
                where=where if where else None,
                limit=max_chunks * 2,
                include=['documents', 'metadatas']
            )
        else:
            # For regex, get all documents and filter in Python
            results = tool.collection.get(
                where=where if where else None,
                limit=max_chunks * 3,
                include=['documents', 'metadatas']
            )
        
        if not results['ids']:
            return {
                "files": [],
                "total_matches": 0,
                "total_files": 0,
                "pattern": pattern
            }
        
        # Group matches by file
        file_matches = defaultdict(list)
        total_matches = 0
        processed_chunks = 0
        
        for doc, meta in zip(results['documents'], results['metadatas']):
            if processed_chunks >= max_chunks:
                break
                
            file_path = meta.get('file_path', 'unknown')
            start_line = meta.get('start_line', 1)
            
            # Find matching lines in chunk
            lines = doc.split('\n')
            for i, line in enumerate(lines):
                matched = False
                
                if use_regex:
                    # Regex matching
                    matched = bool(regex_pattern.search(line))
                else:
                    # Text matching
                    search_line = line if case_sensitive else line.lower()
                    search_pattern = pattern if case_sensitive else pattern.lower()
                    
                    if whole_word:
                        # Whole word matching
                        word_pattern = r'\b' + re.escape(search_pattern) + r'\b'
                        matched = bool(re.search(word_pattern, search_line, re.IGNORECASE if not case_sensitive else 0))
                    else:
                        # Simple substring matching
                        matched = search_pattern in search_line
                
                if matched:
                    line_number = start_line + i
                    
                    # Get context lines if requested
                    context_before = []
                    context_after = []
                    
                    if context_lines > 0:
                        for j in range(max(0, i - context_lines), i):
                            context_before.append(lines[j].strip())
                        for j in range(i + 1, min(len(lines), i + 1 + context_lines)):
                            context_after.append(lines[j].strip())
                    
                    match_data = {
                        'line_number': line_number,
                        'content': line.strip()
                    }
                    
                    if context_lines > 0:
                        match_data['context_before'] = context_before
                        match_data['context_after'] = context_after
                    
                    file_matches[file_path].append(match_data)
                    total_matches += 1
            
            processed_chunks += 1
        
        # Format results
        files = []
        for path in sorted(file_matches.keys()):
            matches = sorted(file_matches[path], key=lambda x: x['line_number'])
            files.append({
                'path': path,
                'matches': matches,
                'match_count': len(matches)
            })
        
        result = {
            'files': files,
            'total_matches': total_matches,
            'total_files': len(files),
            'pattern': pattern,
            'chunks_searched': processed_chunks
        }
        
        logger.debug(f"Found {total_matches} matches in {len(files)} files (searched {processed_chunks} chunks)")
        return result
        
    except Exception as e:
        logger.error(f"Grep search failed: {e}")
        raise RuntimeError(f"Grep search failed: {e}")


def find_function_calls(
    collection_name: str,
    function_name: str,
    language: Optional[str] = None,
    chromadb_dir: Optional[str] = None
) -> Dict:
    """
    Find function calls using language-specific regex patterns.
    
    Args:
        collection_name: ChromaDB collection name
        function_name: Name of function to find calls for
        language: Programming language for pattern optimization
        chromadb_dir: Optional custom ChromaDB directory
        
    Returns:
        Grep search results with function call matches
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty")
    if not function_name:
        raise ValueError("Function name cannot be empty")
    
    # Pattern for function calls: function_name(
    pattern = rf'\b{re.escape(function_name)}\s*\('
    
    return grep_search(
        collection_name=collection_name,
        pattern=pattern,
        use_regex=True,
        language=language,
        chromadb_dir=chromadb_dir
    )


__all__ = ['grep_search', 'find_function_calls']
