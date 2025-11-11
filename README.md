<img src="./docs/banner.webp" alt="Contextinator" width="100%" />
<br />
<h1 align="center">Contextinator <img src="./docs/0banner.png" alt="Contextinator" width="30" /></h1>
<p align="center">
The weapon of mass codebase context for agentic AI. <br />
Turn any codebase into semantically-aware, searchable knowledge for AI-powered workflows.
</p>

---

## 📖 Overview

**Contextinator** is a powerful tool that bridges the gap between static codebases and intelligent AI agents. It uses Abstract Syntax Tree (AST) parsing to extract semantic code chunks, generates embeddings, and stores them in a vector database-enabling AI agents to understand, navigate, and reason about codebases with unprecedented precision.

### ✨ Key Features

- 🌳 **AST-Powered Chunking** - Extract functions, classes, and methods from 23+ programming languages
- 🔍 **Semantic Search** - Find relevant code using natural language queries
- 🚀 **Full Pipeline Automation** - One command to chunk, embed, and store
- 🎯 **Smart Deduplication** - Hash-based detection of duplicate code
- 📊 **Visual AST Explorer** - Debug and visualize code structure
- 📦 **TOON Format Export** - Token-efficient output format for LLM prompts (40-60% savings)

- 🐳 **Docker-Ready** - ChromaDB server included

### 🎯 Use Cases

- **AI Code Assistants** - Give LLMs deep codebase understanding
- **Documentation Generation** - Auto-generate docs from code structure
- **Code Search & Discovery** - Find implementations across large projects
- **Refactoring Analysis** - Identify duplicate or similar code patterns
- **Onboarding Automation** - Help new developers navigate unfamiliar codebases

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker (for ChromaDB)
- OpenAI API key (for embeddings)

### Installation

**Step 1:** Clone and setup

```bash
git clone https://github.com/starthackHQ/Contextinator.git
cd Contextinator
```

**Step 2:** Create virtual environment

```bash
python -m venv .venv
```

**Step 3:** Activate environment

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

**Step 4:** Install dependencies

```bash
pip install -r requirements.txt
```

**Step 5:** Configure environment variables

Copy the example environment file and add your OpenAI API key:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

**Important**: The `.env` file should contain:

```bash
OPENAI_API_KEY=sk-your-openai-key-here
USE_CHROMA_SERVER=true
CHROMA_SERVER_URL=http://localhost:8000
```

**Step 6:** Start ChromaDB

```bash
docker-compose up -d
```

# Usage

this can be used in 2 ways, either via the CLI or programmatically via python code.

## CLI

**Usage:** `python -m src.contextinator.cli <command> [options]`

### 1. Chunking

```bash
python -m src.contextinator.cli chunk --save --path <repo-path> --output <output-dir>
python -m src.contextinator.cli chunk --save --repo-url <github-url>
python -m src.contextinator.cli chunk --save-ast  # Save AST trees for debugging
python -m src.contextinator.cli chunk --chunks-dir <custom-dir>  # Custom chunks directory
```

### 2. Embedding

right now, we're only supporting OpenAI embeddings, so make sure you've got the `.env.example` setup'd correctly.

```bash
python -m src.contextinator.cli embed --save --path <repo-path> --output <output-dir>
python -m src.contextinator.cli embed --save --repo-url <github-url>
python -m src.contextinator.cli embed --chunks-dir <custom-dir> --embeddings-dir <custom-dir>
```

### 3. Storing in Vector Store

**Note:** Make sure ChromaDB server is running: `docker-compose up -d`

```bash
python -m src.contextinator.cli store-embeddings --path <repo-path> --output <output-dir>
python -m src.contextinator.cli store-embeddings --collection-name <custom-name>
python -m src.contextinator.cli store-embeddings --repo-name <repo-name> --collection-name <custom-name>
python -m src.contextinator.cli store-embeddings --embeddings-dir <custom-dir> --chromadb-dir <custom-dir>
```

### 4. Search Commands

Contextinator provides multiple search methods for different use cases:

#### **4.1 Semantic Search** (Natural Language)

Find code using natural language queries. Uses AI embeddings for semantic similarity.

```bash
# Basic semantic search
python -m src.contextinator.cli search "authentication logic" --collection MyRepo

# With filters
python -m src.contextinator.cli search "error handling" -c MyRepo --language python -n 10

# Include parent chunks (classes/modules) in results
python -m src.contextinator.cli search "database queries" -c MyRepo --include-parents

# Filter by file path
python -m src.contextinator.cli search "API endpoints" -c MyRepo --file "src/api/"

# Filter by node type
python -m src.contextinator.cli search "validation logic" -c MyRepo --type function_definition

# Export to JSON
python -m src.contextinator.cli search "authentication" -c MyRepo --json results.json

# Export to TOON format (40-60% token savings for LLMs)
python -m src.contextinator.cli search "authentication" -c MyRepo --toon results.json

**Options:**
- `-c, --collection` (required): Collection name
- `-n, --n-results`: Number of results (default: 5)
- `-l, --language`: Filter by programming language (e.g., python, javascript)
- `-f, --file`: Filter by file path (partial match)
- `-t, --type`: Filter by node type (e.g., function_definition, class_definition)
- `--include-parents`: Include parent chunks (classes/modules) in results
- `--json`: Export results to JSON file
- `--toon`: Export results to TOON file (compact format for LLMs)
```

---

#### **4.2 Symbol Search** (Exact Name Match)

Find specific functions or classes by name.

```bash
# Find function by name
python -m src.contextinator.cli symbol authenticate_user --collection MyRepo

# Find class by name
python -m src.contextinator.cli symbol UserManager -c MyRepo --type class_definition

# Search in specific file
python -m src.contextinator.cli symbol get_user -c MyRepo --file "api/"

# Export results
python -m src.contextinator.cli symbol main -c MyRepo --json main_functions.json

**Options:**
- `-c, --collection` (required): Collection name
- `-t, --type`: Filter by node type
- `-f, --file`: Filter by file path
- `--limit`: Maximum results (default: 50)
- `--json`: Export to JSON
- `--toon`: Export to TOON format
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
python -m src.contextinator.cli search-advanced -c MyRepo \
 --semantic "authentication" --language python

# Pattern search with file filter
python -m src.contextinator.cli search-advanced -c MyRepo \
 --pattern "TODO" --file "src/"

# Hybrid: semantic + pattern + type filter
python -m src.contextinator.cli search-advanced -c MyRepo \
 --semantic "error handling" --pattern "try" --type function_definition

# Multiple filters with export
python -m src.contextinator.cli search-advanced -c MyRepo \
 --semantic "API routes" --language python --file "api/" --toon api_routes.json

**Options:**
- `-c, --collection` (required): Collection name
- `-s, --semantic`: Semantic query (natural language)
- `-p, --pattern`: Text pattern to search for
- `-l, --language`: Filter by programming language
- `-f, --file`: Filter by file path
- `-t, --type`: Filter by node type
- `--limit`: Maximum results (default: 50)
- `--json`: Export to JSON
- `--toon`: Export to TOON format
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
- `--json`: Export to JSON
- `--toon`: Export to TOON format
```

---

### 5. Export Formats

All search commands support two export formats:

#### **JSON Format** (Standard)

```bash
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
python -m src.contextinator.cli search "authentication" -c MyRepo --toon results.json

Perfect for:
- Feeding search results to LLMs
- Building RAG (Retrieval-Augmented Generation) systems
- Minimizing token usage in AI workflows
```

---

### ### 6. Database Management

```bash
# Show database statistics
python -m src.contextinator.cli db-info

# List all collections
python -m src.contextinator.cli db-list

# Show collection details with sample documents
python -m src.contextinator.cli db-show MyRepo --sample 3

# Delete a collection
python -m src.contextinator.cli db-clear MyRepo

# Use custom ChromaDB location
python -m src.contextinator.cli db-info --chromadb-dir <custom-dir>

# Use specific repo database
python -m src.contextinator.cli db-info --repo-name MyRepo
```

---

## 📚 Quick Reference

### Common Workflows

**1. Index a GitHub repository:**

```bash
python -m src.contextinator.cli chunk-embed-store-embeddings \
 --repo-url https://github.com/user/repo \
 --save \
 --collection-name MyRepo
```

**2. Search for specific functionality:**

```bash
# Natural language search
python -m src.contextinator.cli search "how is authentication handled" -c MyRepo

# Find specific function
python -m src.contextinator.cli symbol authenticate_user -c MyRepo

# Find TODOs
python -m src.contextinator.cli pattern "TODO" -c MyRepo
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
