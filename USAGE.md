# Contextinator v2.0 - Complete Usage Guide

This guide is divided into two main sections:

- [**v2 Core Features (Rust-Powered)**](#v2-core-features-rust-powered) - Fast filesystem tools for AI agents (zero dependencies)
- [**RAG Features (Optional)**](#rag-features-optional) - Semantic code search and embeddings (requires `pip install contextinator[rag]`)

---

# v2 Core Features (Rust-Powered)

The core v2 functionality provides blazing-fast filesystem operations built in Rust. **No additional dependencies required.**

## Installation

```bash
# Core installation (Rust-powered tools only)
pip install contextinator

# Verify installation
contextinator --help
contextinator version
```

## CLI Usage - v2 Commands

All v2 commands use the `read` subcommand with different modes:

```bash
contextinator read --path <path> --mode <mode> [options]
```

### 1. Line Mode - Read Files with Line Ranges

Read specific lines from a file, with support for negative indexing.

```bash
# Read lines 10-50
contextinator read --path myfile.py --mode Line --start-line 10 --end-line 50

# Read last 10 lines (negative indexing)
contextinator read --path myfile.py --mode Line --start-line -10 --end-line -1

# Read first 20 lines
contextinator read --path myfile.py --mode Line --start-line 1 --end-line 20

# Read entire file (omit line numbers)
contextinator read --path myfile.py --mode Line

# JSON output
contextinator read --path myfile.py --mode Line --start-line 1 --end-line 50 --format json
```

**Options:**

- `--path` (required): File path to read
- `--mode Line` (required): Line reading mode
- `--start-line`: Starting line number (supports negative indexing)
- `--end-line`: Ending line number (supports negative indexing)
- `--format`: Output format (`text` or `json`, default: `text`)

**Output Format (JSON):**

```json
{
  "type": "line",
  "content": "file contents here...",
  "total_lines": 100,
  "lines_returned": 41
}
```

---

### 2. Directory Mode - List Files and Folders

List directory contents with optional recursive traversal.

```bash
# Non-recursive listing (depth 0)
contextinator read --path src/ --mode Directory --depth 0

# Recursive listing (depth 2)
contextinator read --path src/ --mode Directory --depth 2

# Fully recursive
contextinator read --path . --mode Directory --depth 999

# JSON output for AI agents
contextinator read --path src/ --mode Directory --depth 1 --format json
```

**Options:**

- `--path` (required): Directory path to list
- `--mode Directory` (required): Directory listing mode
- `--depth`: Recursion depth (0 = non-recursive, default: 0)
- `--format`: Output format (`text` or `json`, default: `text`)

**Output Format (JSON):**

```json
{
  "type": "directory",
  "entries": [
    {
      "path": "src/main.py",
      "is_dir": false,
      "size": 2048,
      "modified": 1234567890
    },
    {
      "path": "src/utils/",
      "is_dir": true,
      "size": 0,
      "modified": 1234567890
    }
  ],
  "total_count": 15
}
```

---

### 3. Search Mode - Pattern Matching with Context

Search for text patterns in files with configurable context lines.

```bash
# Find TODOs with context
contextinator read --path . --mode Search --pattern "TODO" --context-lines 2

# Find function definitions
contextinator read --path src/ --mode Search --pattern "def " --context-lines 5

# Find FIXMEs and export to JSON
contextinator read --path . --mode Search --pattern "FIXME" --format json

# Search in specific directory
contextinator read --path src/components/ --mode Search --pattern "useState" --context-lines 3
```

**Options:**

- `--path` (required): Directory or file path to search
- `--mode Search` (required): Search mode
- `--pattern` (required): Text pattern to search for
- `--context-lines`: Number of context lines before/after match (default: 2)
- `--format`: Output format (`text` or `json`, default: `text`)

**Output Format (JSON):**

```json
{
  "type": "search",
  "matches": [
    {
      "file_path": "src/auth.py",
      "line_number": 42,
      "line_content": "    # TODO: implement rate limiting",
      "context_before": [
        "def authenticate_user(username, password):",
        "    \"\"\"Authenticate a user.\"\"\""
      ],
      "context_after": ["    user = get_user(username)", "    if not user:"]
    }
  ],
  "total_matches": 12
}
```

---

## Python API - v2 Functions

Import and use the Rust-powered `fs_read` function directly in your code:

```python
from contextinator import fs_read

# 1. Read file lines
result = fs_read(
    path="myfile.py",
    mode="Line",
    start_line=10,
    end_line=50
)
print(result["content"])
print(f"Lines: {result['lines_returned']}/{result['total_lines']}")

# 2. Read last 10 lines
result = fs_read(
    path="myfile.py",
    mode="Line",
    start_line=-10,
    end_line=-1
)

# 3. List directory (non-recursive)
result = fs_read(
    path="src/",
    mode="Directory",
    depth=0
)
for entry in result["entries"]:
    print(f"{'📁' if entry['is_dir'] else '📄'} {entry['path']}")

# 4. List directory (recursive, depth 2)
result = fs_read(
    path="src/",
    mode="Directory",
    depth=2
)

# 5. Search for patterns
result = fs_read(
    path=".",
    mode="Search",
    pattern="TODO",
    context_lines=2
)
for match in result["matches"]:
    print(f"{match['file_path']}:{match['line_number']}")
    print(f"  {match['line_content']}")
```

### Function Signature

```python
def fs_read(
    path: str,
    mode: str,  # "Line", "Directory", or "Search"
    start_line: Optional[int] = None,  # Line mode only
    end_line: Optional[int] = None,     # Line mode only
    depth: Optional[int] = None,        # Directory mode only (default: 0)
    pattern: Optional[str] = None,      # Search mode only
    context_lines: Optional[int] = None # Search mode only (default: 2)
) -> dict
```

---

## Use Cases for v2 Core

### AI Agent Integration

```python
# Agent reads specific code sections
result = fs_read("src/auth.py", mode="Line", start_line=1, end_line=100)
agent_context = result["content"]

# Agent explores codebase structure
result = fs_read("src/", mode="Directory", depth=2)
file_tree = result["entries"]

# Agent finds TODOs for task planning
result = fs_read(".", mode="Search", pattern="TODO", context_lines=3)
tasks = result["matches"]
```

### Batch File Operations

```python
files_to_read = ["src/main.py", "src/auth.py", "src/api.py"]

for file_path in files_to_read:
    result = fs_read(file_path, mode="Line")
    process_file_content(result["content"])
```

---

# RAG Features (Optional)

# RAG Features (Optional)

For semantic code search, AST-powered chunking, and vector embeddings, install the RAG extras:

```bash
pip install contextinator[rag]
```

## RAG Installation & Setup

**Prerequisites:**

- Docker (for ChromaDB)
- OpenAI API key (for embeddings)

**Install with RAG extras:**

```bash
pip install contextinator[rag]
```

**For development:**

```bash
# Clone and setup
git clone https://github.com/starthackHQ/Contextinator.git
cd Contextinator

# Create virtual environment
python -m venv .venv

# Activate environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install with RAG dependencies
pip install -e ".[rag]"
```

**Configure environment variables:**

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-your-openai-key-here
USE_CHROMA_SERVER=true
CHROMA_SERVER_URL=http://localhost:8000
```

**Start ChromaDB server:**

```bash
docker-compose up -d
```

---

## CLI Usage - RAG Commands

All RAG commands use the `--rag` flag:

```bash
contextinator --rag <command> [options]
```

### 1. Chunking

Extract semantic chunks from code using AST parsing:

```bash
contextinator --rag chunk --save --path <repo-path> --output <output-dir>
contextinator --rag chunk --save --repo-url <github-url>
contextinator --rag chunk --save-ast  # Save AST trees for debugging
contextinator --rag chunk --chunks-dir <custom-dir>  # Custom chunks directory
```

### 2. Embedding

Generate embeddings for code chunks (requires OpenAI API key):

```bash
contextinator --rag embed --save --path <repo-path> --output <output-dir>
contextinator --rag embed --save --repo-url <github-url>
contextinator --rag embed --chunks-dir <custom-dir> --embeddings-dir <custom-dir>
```

### 3. Storing in Vector Store

**Note:** Make sure ChromaDB server is running: `docker-compose up -d`

```bash
contextinator --rag store-embeddings --path <repo-path> --output <output-dir>
contextinator --rag store-embeddings --collection-name <custom-name>
contextinator --rag store-embeddings --repo-name <repo-name> --collection-name <custom-name>
contextinator --rag store-embeddings --embeddings-dir <custom-dir> --chromadb-dir <custom-dir>
```

### 4. Search Commands

Contextinator RAG provides multiple search methods for different use cases:

#### **4.1 Semantic Search** (Natural Language)

Find code using natural language queries. Uses AI embeddings for semantic similarity.

```bash
# Basic semantic search
contextinator --rag search "authentication logic" --collection MyRepo

# With filters
contextinator --rag search "error handling" -c MyRepo --language python -n 10

# Include parent chunks (classes/modules) in results
contextinator --rag search "database queries" -c MyRepo --include-parents

# Filter by file path
contextinator --rag search "API endpoints" -c MyRepo --file "src/api/"

# Filter by node type
contextinator --rag search "validation logic" -c MyRepo --type function_definition

# Export to JSON
contextinator --rag search "authentication" -c MyRepo --json results.json

# Export to TOON format (40-60% token savings for LLMs)
contextinator --rag search "authentication" -c MyRepo --toon results.json results
- `--json`: Export results to JSON file
- `--toon`: Export results to TOON file (compact format for LLMs)
```

---

#### **4.2 Symbol Search** (Exact Name Match)

Find specific functions or classes by name.

```bash
# Find function by name
contextinator --rag symbol authenticate_user --collection MyRepo

# Find class by name
contextinator --rag symbol UserManager -c MyRepo --type class_definition

# Search in specific file
contextinator --rag symbol get_user -c MyRepo --file "api/"

# Export results
contextinator --rag symbol main -c MyRepo --json main_functions.json
```

---

#### **4.3 Pattern Search** (Text/Regex)

Search for specific text patterns in code.

```bash
# Find TODOs
python -m src.contextinator.cli pattern "TODO" --collection MyRepo

# Find import statements
python -m src.contextinator.cli pattern "import requests" -c MyRepo --language python

# Find async functions
python -m src.contextinator.cli pattern "async def" -c MyRepo --file "api/"

# Find FIXMEs and export
python -m src.contextinator.cli pattern "FIXME" -c MyRepo --toon fixmes.json

**Options:**
- `-c, --collection` (required): Collection name
- `-l, --language`: Filter by programming language
- `-f, --file`: Filter by file path
- `-t, --type`: Filter by node type
- `--limit`: Maximum results (default: 50)
- `--json`: Export to JSON
- `--toon`: Export to TOON format
```

---

#### **4.4 Advanced Search** (Hybrid)

Combine semantic search, pattern matching, and filters for precise results.

```bash
# Semantic search with language filter
contextinator --rag search-advanced -c MyRepo \
 --semantic "authentication" --language python

# Pattern search with file filter
contextinator --rag search-advanced -c MyRepo \
 --pattern "TODO" --file "src/"

# Hybrid: semantic + pattern + type filter
contextinator --rag search-advanced -c MyRepo \
 --semantic "error handling" --pattern "try" --type function_definition

# Multiple filters with export
contextinator --rag search-advanced -c MyRepo \
 --semantic "API routes" --language python --file "api/" --toon api_routes.json
```

---

#### **4.5 Read File** (Reconstruct from Chunks)

Reconstruct and display a complete file from its chunks.

```bash
# Read complete file
python -m src.contextinator.cli read-file "src/auth.py" --collection MyRepo

# Show chunks separately (don't join)
python -m src.contextinator.cli read-file "src/api/routes.py" -c MyRepo --no-join

# Export to JSON
python -m src.contextinator.cli read-file "src/main.py" -c MyRepo --json main.json

**Options:**
- `-c, --collection` (required): Collection name
- `--no-join`: Show chunks separately instead of joining them
contextinator --rag read-file "src/auth.py" --collection MyRepo

# Show chunks separately (don't join)
contextinator --rag read-file "src/api/routes.py" -c MyRepo --no-join

# Export to JSON
contextinator --rag read-file "src/main.py" -c MyRepo --json main.json
python -m src.contextinator.cli search "authentication" -c MyRepo --json results.json

Output structure:
json
{
 "query": "authentication",
 "collection": "MyRepo",
 "total_results": 5,
 "results": [
   {
     "id": "chunk_0_12345",
     "content": "def authenticate_user(username, password):\n    ...",
     "metadata": {
       "file_path": "src/auth.py",
       "language": "python",
       "node_type": "function_definition",
       "node_name": "authenticate_user",
       "start_line": 10,
       "end_line": 25
     },
     "cosine_similarity": 0.89
   }
 ]
}
```

#### **TOON Format** (Token-Optimized)

Compact format designed for LLM prompts. Saves 40-60% tokens compared to JSON.

```bash
contextinator --rag search "authentication" -c MyRepo --toon results.json
```

Perfect for:

- Feeding search results to LLMs
- Building RAG (Retrieval-Augmented Generation) systems
- Minimizing token usage in AI workflows

---

### 6. Database Management

```bash
# Show database statistics
contextinator --rag db-info

# List all collections
contextinator --rag db-list

# Show collection details with sample documents
contextinator --rag db-show MyRepo --sample 3

# Delete a collection
contextinator --rag db-clear MyRepo

# Use custom ChromaDB location
contextinator --rag db-info --chromadb-dir <custom-dir>

# Use specific repo database
contextinator --rag db-info --repo-name MyRepo
```

---

## 📦 RAG Programmatic Usage (As a Library)

You can also import and use Contextinator RAG features directly in your Python code:

```python
from contextinator.rag import (
    chunk_repository,
    embed_chunks,
    store_repository_embeddings,
    semantic_search,
    symbol_search,
    read_file,
)

# 1. Chunk a repository
chunks = chunk_repository(
    repo_path="./my-project",
    repo_name="MyProject",
    save=True,
    output_dir="./output"
)
print(f"Created {len(chunks)} chunks")

# 2. Generate embeddings
embeddings = embed_chunks(
    base_dir="./output",
    repo_name="MyProject",
    save=True
)

# 3. Store in vector database
stats = store_repository_embeddings(
    base_dir="./output",
    repo_name="MyProject",
    embedded_chunks=embeddings,
    collection_name="MyProject"
)
print(f"Stored {stats['stored_count']} embeddings")

# 4. Search semantically
results = semantic_search(
    collection_name="MyProject",
    query="authentication logic",
    n_results=5
)

for result in results:
    print(f"File: {result['metadata']['file_path']}")
    print(f"Code: {result['content'][:200]}...")
    print(f"Similarity: {result.get('cosine_similarity', 'N/A')}")
    print("-" * 80)

# 5. Search by symbol name
functions = symbol_search(
    collection_name="MyProject",
    symbol_name="authenticate_user"
)

# 6. Read entire file from chunks
file_content = read_file(
    collection_name="MyProject",
    file_path="src/auth.py"
)
print(file_content['content'])
```

---

## 📚 Quick Reference

### Common Workflows

**1. Index a GitHub repository:**

```bash
contextinator chunk-embed-store-embeddings \
 --repo-url https://github.com/user/repo \
 --save \
 --collection-name MyRepo
```

**2. Search for specific functionality:**

```bash
# Natural language search
contextinator search "how is authentication handled" -c MyRepo

# Find specific function
contextinator symbol authenticate_user -c MyRepo

# Find TODOs
contextinator pattern "TODO" -c MyRepo
```

**3. Advanced filtered search:**

```bash
python -m src.contextinator.cli search-advanced -c MyRepo \
 --semantic "error handling" \
 --language python \
 --file "src/" \
 --toon error_handling.json
```

**4. Export for LLM context:**

```bash
# Get authentication-related code in token-efficient format
python -m src.contextinator.cli search "authentication and authorization" \
 -c MyRepo \
 --include-parents \
 --toon auth_context.json
```

### All Commands

| Command                        | Purpose                            | Example                                                          |
| ------------------------------ | ---------------------------------- | ---------------------------------------------------------------- |
| `chunk`                        | Extract semantic chunks from code  | `chunk --repo-url <url> --save`                                  |
| `embed`                        | Generate embeddings for chunks     | `embed --repo-url <url> --save`                                  |
| `store-embeddings`             | Store embeddings in ChromaDB       | `store-embeddings --repo-name MyRepo`                            |
| `chunk-embed-store-embeddings` | Full pipeline (all-in-one)         | `chunk-embed-store-embeddings --repo-url <url> --save`           |
| `search`                       | Semantic search (natural language) | `search "query" -c MyRepo`                                       |
| `symbol`                       | Find functions/classes by name     | `symbol function_name -c MyRepo`                                 |
| `pattern`                      | Text/regex search                  | `pattern "TODO" -c MyRepo`                                       |
| `search-advanced`              | Hybrid search with filters         | `search-advanced -c MyRepo --semantic "query" --language python` |
| `read-file`                    | Reconstruct file from chunks       | `read-file "path/to/file.py" -c MyRepo`                          |
| `db-info`                      | Show database statistics           | `db-info`                                                        |
| `db-list`                      | List all collections               | `db-list`                                                        |
| `db-show`                      | Show collection details            | `db-show MyRepo --sample 3`                                      |
| `db-clear`                     | Delete a collection                | `db-clear MyRepo`                                                |
