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

Generates embeddings for chunks using OpenAI's text-embedding-3-large model.

**Options:**
- `--save`: Save embeddings to `.embeddings/embeddings.json`
- `--path PATH`: Path to repository (default: current directory)
- `--repo-url URL`: Clone and embed remote repository

**Examples:**
```bash
python -m src.cli embed --save
python -m src.cli embed --save --path /path/to/repo
```

**Requirements:**
- Set `OPENAI_API_KEY` in `.env` file
- Chunks must exist (run `chunk --save` first)

### `store-embeddings`

Loads embeddings into ChromaDB vector store.

**Options:**
- `--path PATH`: Path to repository (default: current directory)
- `--repo-url URL`: Remote repository URL
- `--collection-name NAME`: Custom collection name (default: repository name)

**Examples:**
```bash
python -m src.cli store-embeddings --path .
python -m src.cli store-embeddings --path . --collection-name MyProject
```

**Requirements:**
- ChromaDB server running (Docker): `docker-compose up -d`
- Embeddings must exist (run `embed --save` first)

### `chunk-embed-store-embeddings`

Full pipeline: chunk → embed → store in one command.

**Options:**
- `--save`: Save intermediate artifacts (chunks + embeddings)
- `--path PATH`: Path to repository (default: current directory)
- `--repo-url URL`: Clone and process remote repository
- `--collection-name NAME`: Custom collection name

**Examples:**
```bash
# Process current directory
python -m src.cli chunk-embed-store-embeddings --save

# Process remote repository
python -m src.cli chunk-embed-store-embeddings --save --repo-url https://github.com/user/repo

# Custom collection name
python -m src.cli chunk-embed-store-embeddings --save --collection-name MyProject
```

### `db-info`

Show ChromaDB database information and statistics.

**Examples:**
```bash
python -m src.cli db-info
```

**Output:**
- List of all collections
- Document counts per collection
- Total documents across all collections

### `db-list`

List all collections in ChromaDB.

**Examples:**
```bash
python -m src.cli db-list
```

### `db-show`

Show details of a specific collection.

**Options:**
- `collection_name`: Name of the collection (required)
- `--sample N`: Show N sample documents

**Examples:**
```bash
python -m src.cli db-show SemanticSage
python -m src.cli db-show SemanticSage --sample 5
```

### `db-clear`

Delete a specific collection from ChromaDB.

**Options:**
- `collection_name`: Name of the collection to delete (required)
- `--force`: Skip confirmation prompt

**Examples:**
```bash
python -m src.cli db-clear SemanticSage
python -m src.cli db-clear SemanticSage --force
```

### `query`

⚠️ **Not yet implemented** - Semantic search on vector store.

```bash
python -m src.cli query "implement user authentication in Python"
python -m src.cli query "myquery" --save results.txt --n-results 10
```

# ChromaDB Setup

## Start ChromaDB Server (Docker)

```bash
# Start ChromaDB server
docker-compose up -d

# Check if running
docker ps | grep chroma

# Stop server
docker-compose down
```

## View Your Data

### Web Viewer (Recommended)

Start the web viewer to browse your embeddings:

```bash
python viewer.py
```

Then open: **http://localhost:5001**

Features:
- Browse all collections
- View chunks with metadata (file path, type, line numbers)
- Paginated navigation
- Clean, simple interface

### CLI Viewer

Use CLI commands to inspect data:

```bash
# Show collection info
python -m src.cli db-info

# List all collections
python -m src.cli db-list

# Show specific collection with samples
python -m src.cli db-show SemanticSage --sample 5
```

## Environment Configuration

Create a `.env` file in the project root:

```bash
# OpenAI API Key (required for embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# ChromaDB Configuration
USE_CHROMA_SERVER=true
CHROMA_SERVER_URL=http://localhost:8000
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
