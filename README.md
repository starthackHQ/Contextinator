# Code Semantic Search Experiment

This repository contains an experimental setup for performing semantic search on a code base. The goal is to enable efficient and accurate retrieval of code snippets based on natural language queries.

# Project Setup

1. Clone the repository
2. Set up a Python virtual environment using `python -m venv .venv`
3. Activate the virtual environment:
   - On Windows: `.venv\Scripts\activate`
   - On macOS/Linux: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

# Quick Start: Generate Code Chunks

## 1. Chunk Your Local Repository

```bash
# Chunk current directory - saves to .chunks/chunks.json
python -m src.cli chunk --save

# Chunk with AST visualization (recommended for debugging)
python -m src.cli chunk --save --save-ast

# Chunk specific directory
python -m src.cli chunk --save --path /path/to/your/repo

# Custom output location
python -m src.cli chunk --save --output /custom/output/dir
```

## 2. Chunk Remote Repository

```bash
# Clone and chunk a GitHub repository
python -m src.cli chunk --save --repo-url https://github.com/username/repo

# With AST visualization
python -m src.cli chunk --save --save-ast --repo-url https://github.com/username/repo
```

## 3. Understanding the Output

After running `chunk --save`, you'll find:

```
.chunks/
├── chunks.json          # All extracted code chunks with metadata
└── ast_trees/          # AST visualizations (if --save-ast used)
    ├── file1_python_ast.json
    ├── file2_javascript_ast.json
    └── ast_overview.json
```

**chunks.json structure:**
```json
{
  "chunks": [
    {
      "type": "function_definition",
      "name": "my_function",
      "content": "def my_function():\n    return 'hello'",
      "file_path": "/path/to/file.py",
      "language": "python",
      "start_line": 10,
      "end_line": 12,
      "hash": "abc123..."
    }
  ],
  "statistics": {
    "unique_hashes": 150,
    "duplicates_found": 5
  }
}
```

## Supported Languages (23)

Python, JavaScript, TypeScript, TSX, Java, Go, Rust, C, C++, C#, PHP, Bash, SQL, Kotlin, YAML, Markdown, Dockerfile, JSON, TOML, Swift, Solidity, Lua

Each language extracts semantic units like:
- **Functions/Methods**: Function definitions, arrow functions, method declarations
- **Classes**: Class declarations, interfaces, structs
- **Other**: Properties, objects, tables, commands (language-specific)

# CLI Reference

## Available Commands

### `chunk --save`

Chunks the codebase into semantic units using Tree-sitter AST parsing.

**Options:**
- `--save`: Save chunks to `.chunks/chunks.json`
- `--save-ast`: Generate AST visualizations for debugging
- `--path PATH`: Path to repository (default: current directory)
- `--output DIR`: Output directory (default: current directory)
- `--repo-url URL`: Clone and chunk remote repository

**Examples:**
```bash
python -m src.cli chunk --save
python -m src.cli chunk --save --save-ast
python -m src.cli chunk --save --repo-url https://github.com/user/repo
```

### `embed --save`

⚠️ **Not yet implemented** - Generates embeddings for chunks.

```bash
python -m src.cli embed --save
python -m src.cli embed --save --model-name-or-path your-model --batch-size 16
```

### `store-embeddings --vectorstore chroma`

⚠️ **Not yet implemented** - Loads embeddings into vector store.

```bash
python -m src.cli store-embeddings --vectorstore chroma
python -m src.cli store-embeddings --vectorstore chroma --db-path .chroma_db
```

### `chunk-embed-store-embeddings`

⚠️ **Not yet implemented** - Full pipeline in one command.

```bash
python -m src.cli chunk-embed-store-embeddings --save --vectorstore chroma
```

### `query`

⚠️ **Not yet implemented** - Semantic search on vector store.

```bash
python -m src.cli query "implement user authentication in Python"
python -m src.cli query "myquery" --save results.txt --n-results 10
```

# Advanced Features

## AST Visualization

Enable AST visualization to see how your code is parsed:

```bash
python -m src.cli chunk --save --save-ast
```

**Output structure:**
```
.chunks/ast_trees/
├── MyFile_python_ast.json     # Individual file AST
├── AnotherFile_java_ast.json
└── ast_overview.json          # Summary of all files
```

**AST file contents:**
- Complete AST tree structure
- Extracted semantic nodes (functions, classes)
- Tree statistics (depth, node count)
- Source code mappings (line numbers, byte positions)

## Ignore Patterns

The tool automatically ignores common build artifacts and dependencies:

- **Python**: `__pycache__`, `.venv`, `*.pyc`, `.pytest_cache`
- **JavaScript/Node**: `node_modules`, `*.min.js`, `.next`, lock files
- **Java/Kotlin**: `target`, `*.class`, `.gradle`
- **C/C++**: `*.o`, `*.so`, `CMakeFiles`
- **Rust**: `target`, `Cargo.lock`
- **Go**: `vendor`
- **C#/.NET**: `bin`, `obj`, `.vs`
- **PHP**: `vendor`, `composer.lock`
- **Swift**: `.build`, `DerivedData`
- **General**: `.git`, `.idea`, `.vscode`, `*.log`

See `src/config/settings.py` for the complete list.

## Configuration

Edit `src/config/settings.py` to customize:

```python
MAX_TOKENS = 512              # Maximum tokens per chunk
CHUNK_OVERLAP = 50            # Overlap between chunks
DEFAULT_EMBEDDING_MODEL = '...'  # Embedding model (future use)
```

# Installation

Install all dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install tree-sitter chromadb \
  tree-sitter-python tree-sitter-javascript tree-sitter-typescript \
  tree-sitter-java tree-sitter-go tree-sitter-rust \
  tree-sitter-cpp tree-sitter-c tree-sitter-c-sharp \
  tree-sitter-php tree-sitter-bash tree-sitter-sql \
  tree-sitter-kotlin tree-sitter-yaml tree-sitter-markdown \
  tree-sitter-dockerfile tree-sitter-json tree-sitter-toml \
  tree-sitter-swift tree-sitter-solidity tree-sitter-lua
```

# Troubleshooting

**No chunks generated?**
- Check if your files have supported extensions
- Verify files aren't in ignore patterns
- Use `--save-ast` to debug AST parsing

**Tree-sitter import errors?**
- Install missing language modules: `pip install tree-sitter-<language>`
- The tool will fallback to file-level chunking if parsers are missing

**Empty chunks.json?**
- Ensure you're in a directory with code files
- Check that file extensions match `SUPPORTED_EXTENSIONS` in settings.py
