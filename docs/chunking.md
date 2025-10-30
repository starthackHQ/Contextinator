# Chunking
The chunking process is a crucial step in preparing code files for indexing and search. It involves breaking down code into manageable, semantically meaningful pieces called "chunks." This document outlines the chunking strategy employed, including AST-based semantic chunking, content deduplication, token-based splitting, and metadata enrichment.


## Key Features
1. AST-Based Semantic Chunking
- Uses Tree-sitter to parse code into semantic units (functions, classes, methods)
- Extracts specific node types per language (e.g., function_definition for Python)
- Falls back to file-level chunking if Tree-sitter unavailable

2. Content Deduplication
- Uses SHA256 hashing to deduplicate identical code blocks
- Tracks all locations where duplicates appear
- Reduces storage and improves search efficiency

3. Token-Based Splitting
- Splits large chunks exceeding 512 tokens
- Maintains 50-token overlap between splits
- Preserves original metadata in split chunks

4. Rich Metadata
- File path, language, node type/name
- Precise line and byte positioning
- Hash for deduplication
- Location tracking for duplicates




## Current Chunk Structure
Each chunk in the system is a dictionary with the following structure:
```json
{
  "content": "def my_function():\n    return 'hello'",
  "file_path": "/path/to/file.py", 
  "language": "python",
  "hash": "abc123...",
  "node_type": "function_definition",
  "node_name": "my_function",
  "start_line": 10,
  "end_line": 12,
  "start_byte": 150,
  "end_byte": 180,
  "locations": ["/path/to/file.py:10-12"]
}
```

### Additional Fields for Split Chunks
When chunks exceed `MAX_TOKENS` (512), they get split and gain additional fields:
```json
{
  // ... all above fields
  "is_split": true,
  "split_index": 0,
  "original_hash": "original_chunk_hash"
}
```

## Storage Format
Chunks are saved to `.chunks/chunks.json` with this wrapper structure:
```json
{
  "chunks": [/* array of chunk objects */],
  "statistics": {
    "total_chunks": 150,
    "unique_hashes": 145,
    "duplicates_found": 5,
    "duplicate_locations": {
      "hash123": ["/file1.py:10-15", "/file2.py:20-25"]
    }
  }
}
```