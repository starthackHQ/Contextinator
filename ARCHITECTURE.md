# SemanticSage Architecture

## Module Structure

```
src/
├── cli.py                          # CLI interface
├── chunk.py                        # Main chunking orchestrator
├── embed.py                        # Embedding generation (TODO)
├── query.py                        # Query interface (TODO)
├── vectorstore.py                  # Vector DB operations (TODO)
│
├── chunking/                       # Chunking modules
│   ├── __init__.py
│   ├── file_discovery.py          # File discovery & filtering
│   ├── ast_parser.py              # AST parsing with tree-sitter
│   ├── node_collector.py          # Collect & deduplicate nodes
│   ├── splitter.py                # Split large chunks
│   └── context_builder.py         # Build context for chunks
│
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── token_counter.py           # Token counting
│   ├── hash_utils.py              # Hashing for deduplication
│   └── progress.py                # Progress tracking
│
└── config/                         # Configuration
    ├── __init__.py
    └── settings.py                # Configuration constants
```

## Chunking Pipeline

### 1. File Discovery (`file_discovery.py`)
- Walks repository directory tree
- Filters by supported extensions (`.py`, `.js`, `.ts`, etc.)
- Respects ignore patterns (node_modules, .git, etc.)
- Returns list of files to process

### 2. AST Parsing (`ast_parser.py`)
- Parses each file using tree-sitter (TODO: implement)
- Currently returns basic file structure
- Handles parse errors gracefully
- Returns AST + metadata

### 3. Node Collection (`node_collector.py`)
- Traverses AST to extract semantic units
- Deduplicates by content hash (SHA256)
- Tracks all occurrences of duplicates
- Returns unique chunks with metadata

### 4. Chunk Splitting (`splitter.py`)
- Splits chunks exceeding `MAX_TOKENS`
- Line-by-line splitting with token counting
- Configurable overlap between splits
- Preserves metadata in split chunks

### 5. Context Building (`context_builder.py`)
- Builds contextual information for chunks
- Includes file path, language, node type, line range
- Used for better retrieval and display

## Configuration (`config/settings.py`)

```python
MAX_TOKENS = 512              # Maximum tokens per chunk
CHUNK_OVERLAP = 50            # Token overlap between splits
SUPPORTED_EXTENSIONS = {...}  # File extensions to process
DEFAULT_IGNORE_PATTERNS = [...] # Patterns to ignore
```

## Current Status

### ✅ Implemented
- Modular architecture
- File discovery with filtering
- Basic file parsing
- Content deduplication
- Chunk splitting with overlap
- Progress tracking
- CLI integration

### 🚧 TODO
- Tree-sitter AST parsing (currently treats files as single chunks)
- Better token counting (use tiktoken)
- Embedding generation (`embed.py`)
- Vector store integration (`vectorstore.py`)
- Query functionality (`query.py`)
- GitHub repo cloning support
- Parallel processing
- Incremental updates

## Usage

```bash
# Chunk current repository
python -m src.cli chunk --save

# View chunks
cat .chunks/chunks.json
```

## Next Steps

1. Implement tree-sitter AST parsing for semantic chunking
2. Add embedding generation with sentence-transformers
3. Integrate ChromaDB for vector storage
4. Implement query functionality
5. Add GitHub repo URL support
