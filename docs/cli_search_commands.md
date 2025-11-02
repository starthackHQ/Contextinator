# CLI Search Commands Reference

## Quick Start

All search commands require a `--collection` (or `-c`) argument specifying the ChromaDB collection name.

```bash
# List available collections
python -m src.contextinator.cli db-list
```

---

## Commands

### 1. `search` - Semantic Search

Natural language queries using cosine similarity.

**Syntax:**

```bash
python -m src.contextinator.cli search "query text" --collection COLLECTION [OPTIONS]
```

**Examples:**

```bash
# Basic semantic search
python -m src.contextinator.cli search "How is authentication handled?" -c my-repo

# Filter by language
python -m src.contextinator.cli search "database connection" -c my-repo --language python

# Get more results
python -m src.contextinator.cli search "error handling" -c my-repo -n 10

# Filter by file
python -m src.contextinator.cli search "API endpoints" -c my-repo --file routes.py

# Export to JSON
python -m src.contextinator.cli search "auth logic" -c my-repo --json results.json
```

**Options:**

- `--collection`, `-c` - Collection name (required)
- `--n-results`, `-n` - Number of results (default: 5)
- `--language`, `-l` - Filter by programming language
- `--file`, `-f` - Filter by file path (partial match)
- `--type`, `-t` - Filter by node type
- `--json` - Export to JSON file

---

### 2. `symbol` - Find Symbols

Find specific functions, classes, or symbols by name.

**Syntax:**

```bash
python -m src.contextinator.cli symbol SYMBOL_NAME --collection COLLECTION [OPTIONS]
```

**Examples:**

```bash
# Find a class
python -m src.contextinator.cli symbol UserController -c my-repo

# Find function with type filter
python -m src.contextinator.cli symbol authenticate -c my-repo --type function_definition

# Find in specific file
python -m src.contextinator.cli symbol validate -c my-repo --file auth.py

# Export results
python -m src.contextinator.cli symbol MyClass -c my-repo --json output.json
```

**Options:**

- `--collection`, `-c` - Collection name (required)
- `--type`, `-t` - Filter by node type
- `--file`, `-f` - Filter by file path
- `--limit` - Maximum results (default: 50)
- `--json` - Export to JSON file

---

### 3. `pattern` - Pattern Search

Search for code patterns (substring matching).

**Syntax:**

```bash
python -m src.contextinator.cli pattern "PATTERN" --collection COLLECTION [OPTIONS]
```

**Examples:**

```bash
# Find function calls
python -m src.contextinator.cli pattern "authenticate(" -c my-repo

# Find TODO comments in Python
python -m src.contextinator.cli pattern "TODO" -c my-repo --language python

# Find imports in specific file
python -m src.contextinator.cli pattern "import" -c my-repo --file auth.py

# Complex pattern with filters
python -m src.contextinator.cli pattern "async def" -c my-repo --language python --limit 20
```

**Options:**

- `--collection`, `-c` - Collection name (required)
- `--language`, `-l` - Filter by programming language
- `--file`, `-f` - Filter by file path
- `--type`, `-t` - Filter by node type
- `--limit` - Maximum results (default: 50)
- `--json` - Export to JSON file

---

### 4. `read-file` - Reconstruct Files

View complete files reconstructed from chunks.

**Syntax:**

```bash
python -m src.contextinator.cli read-file FILE_PATH --collection COLLECTION [OPTIONS]
```

**Examples:**

```bash
# Read complete file
python -m src.contextinator.cli read-file src/auth.py -c my-repo

# Show chunks separately
python -m src.contextinator.cli read-file auth.py -c my-repo --no-join

# Export to JSON
python -m src.contextinator.cli read-file main.py -c my-repo --json file_content.json
```

**Options:**

- `--collection`, `-c` - Collection name (required)
- `--no-join` - Show chunks separately (don't join)
- `--json` - Export to JSON file

---

### 5. `search-advanced` - Advanced Search

Complex queries with multiple criteria or hybrid search.

**Syntax:**

```bash
python -m src.contextinator.cli search-advanced --collection COLLECTION [OPTIONS]
```

**Examples:**

```bash
# Hybrid semantic + metadata search
python -m src.contextinator.cli search-advanced -c my-repo --semantic "auth logic" --language python

# Pattern with metadata filters
python -m src.contextinator.cli search-advanced -c my-repo --pattern "import" --file auth.ts

# Get all Python functions
python -m src.contextinator.cli search-advanced -c my-repo --type function_definition --language python

# Complex filters
python -m src.contextinator.cli search-advanced -c my-repo \
  --semantic "database queries" \
  --language python \
  --file models/ \
  --limit 20
```

**Options:**

- `--collection`, `-c` - Collection name (required)
- `--semantic`, `-s` - Semantic query (enables hybrid search)
- `--pattern`, `-p` - Text pattern to search
- `--language`, `-l` - Filter by programming language
- `--file`, `-f` - Filter by file path
- `--type`, `-t` - Filter by node type
- `--limit` - Maximum results (default: 50)
- `--json` - Export to JSON file

---

## Common Workflows

### Find and Understand Code

```bash
# 1. Find relevant code semantically
python -m src.contextinator.cli search "user authentication flow" -c my-repo

# 2. Find specific function
python -m src.contextinator.cli symbol authenticate -c my-repo

# 3. Find all calls to that function
python -m src.contextinator.cli pattern "authenticate(" -c my-repo

# 4. Read the complete file
python -m src.contextinator.cli read-file src/auth.py -c my-repo
```

### Code Analysis

```bash
# Find all TODO comments
python -m src.contextinator.cli pattern "TODO" -c my-repo --json todos.json

# Get all Python classes
python -m src.contextinator.cli search-advanced -c my-repo \
  --type class_definition \
  --language python \
  --json classes.json

# Find error handling patterns
python -m src.contextinator.cli search "error handling and exceptions" -c my-repo -n 10
```

### File Exploration

```bash
# List all files (via db-show)
python -m src.contextinator.cli db-show my-repo --sample 100

# Read specific file
python -m src.contextinator.cli read-file src/main.py -c my-repo

# Find all imports in a file
python -m src.contextinator.cli pattern "import" -c my-repo --file main.py
```

---

## Output Formats

### Console Output (Default)

```
🔍 Search Results: "How is authentication handled?"
Collection: my-repo
Found: 3 results

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Result 1/3 | Similarity: 0.892
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 File: src/auth/authenticate.py
🏷️  Type: function_definition | Symbol: authenticate
📍 Lines: 45-67

def authenticate(username, password):
    """Authenticate user credentials."""
    ...
```

### JSON Output (--json flag)

```json
{
  "query": "How is authentication handled?",
  "collection": "my-repo",
  "total_results": 3,
  "results": [
    {
      "id": "chunk_123",
      "content": "def authenticate(...)...",
      "metadata": {
        "file_path": "src/auth/authenticate.py",
        "language": "python",
        "node_type": "function_definition",
        "node_name": "authenticate",
        "start_line": 45,
        "end_line": 67
      },
      "cosine_similarity": 0.892
    }
  ]
}
```

---

## Tips

1. **Use semantic search** for conceptual queries
2. **Use symbol search** for exact names
3. **Use pattern search** for code patterns
4. **Combine filters** for precise results
5. **Export to JSON** for programmatic processing
6. **Check similarity scores** - higher is better (0-1 range)

---

## Help

Get help for any command:

```bash
python -m src.contextinator.cli search --help
python -m src.contextinator.cli symbol --help
python -m src.contextinator.cli pattern --help
python -m src.contextinator.cli read-file --help
python -m src.contextinator.cli search-advanced --help
```
