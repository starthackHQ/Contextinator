This file is broken into 2 sections
- [Installation](#installation)
- [Usage](#usage)

# Installation
Normal installation can be done via pip; see README.md for basic instructions.
For development and advanced setup, follow these steps:

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
Contextinator can be used in **two ways**: via the **CLI** or **programmatically** as a Python library.

## CLI Usage
After installation, you can use the `contextinator` command directly:

```bash
# Recommended: Use the installed command
contextinator <command> [options]

# Alternative: Use module execution
python -m contextinator <command> [options]
```

**Development mode** (before installation):

```bash
python -m src.contextinator <command> [options]
```

### 1. Chunking

```bash
contextinator chunk --save --path <repo-path> --output <output-dir>
contextinator chunk --save --repo-url <github-url>
contextinator chunk --save-ast  # Save AST trees for debugging
contextinator chunk --chunks-dir <custom-dir>  # Custom chunks directory
```

### 2. Embedding

right now, we're only supporting OpenAI embeddings, so make sure you've got the `.env.example` setup'd correctly.

```bash
contextinator embed --save --path <repo-path> --output <output-dir>
contextinator embed --save --repo-url <github-url>
contextinator embed --chunks-dir <custom-dir> --embeddings-dir <custom-dir>
```

### 3. Storing in Vector Store

**Note:** Make sure ChromaDB server is running: `docker-compose up -d`

```bash
contextinator store-embeddings --path <repo-path> --output <output-dir>
contextinator store-embeddings --collection-name <custom-name>
contextinator store-embeddings --repo-name <repo-name> --collection-name <custom-name>
contextinator store-embeddings --embeddings-dir <custom-dir> --chromadb-dir <custom-dir>
```

### 4. Search Commands

Contextinator provides multiple search methods for different use cases:

#### **4.1 Semantic Search** (Natural Language)

Find code using natural language queries. Uses AI embeddings for semantic similarity.

```bash
# Basic semantic search
contextinator search "authentication logic" --collection MyRepo

# With filters
contextinator search "error handling" -c MyRepo --language python -n 10

# Include parent chunks (classes/modules) in results
contextinator search "database queries" -c MyRepo --include-parents

# Filter by file path
contextinator search "API endpoints" -c MyRepo --file "src/api/"

# Filter by node type
contextinator search "validation logic" -c MyRepo --type function_definition

# Export to JSON
contextinator search "authentication" -c MyRepo --json results.json

# Export to TOON format (40-60% token savings for LLMs)
contextinator search "authentication" -c MyRepo --toon results.json

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

### 6. Database Management

```bash
# Show database statistics
contextinator db-info

# List all collections
contextinator db-list

# Show collection details with sample documents
contextinator db-show MyRepo --sample 3

# Delete a collection
contextinator db-clear MyRepo

# Use custom ChromaDB location
contextinator db-info --chromadb-dir <custom-dir>

# Use specific repo database
contextinator db-info --repo-name MyRepo
```

---

## 📦 Programmatic Usage (As a Library)

You can also import and use Contextinator directly in your Python code:

```python
from contextinator import (
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
