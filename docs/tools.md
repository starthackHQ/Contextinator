# Search Tools Documentation

## Overview

The `src/tools/` module provides 5 powerful search tools for querying ChromaDB collections. All tools use **cosine similarity** for semantic search and support flexible metadata filtering.

---

## 🔍 Available Tools

### 1. Symbol Search (`symbol_search.py`)

Find specific functions, classes, or symbols by name.

**Functions:**
- `symbol_search()` - Find symbols by exact name match
- `list_symbols()` - List all unique symbol names

**Use Cases:**
- Find class definitions
- Locate specific functions
- Search for methods by name

**Example:**
```python
from src.tools import symbol_search

# Find UserController class
results = symbol_search("my-repo", "UserController", node_type="class_declaration")

# Find all validate functions
results = symbol_search("my-repo", "validate", node_type="function_definition")

# Find symbol in specific file
results = symbol_search("my-repo", "authenticate", file_path="auth.py")
```

---

### 2. Regex Search (`regex_search.py`)

Pattern-based search in code content.

**Functions:**
- `regex_search()` - Search for text patterns in code
- `find_function_calls()` - Find all calls to a specific function

**Use Cases:**
- Find function calls
- Locate TODO/FIXME comments
- Search for specific code patterns

**Example:**
```python
from src.tools import regex_search, find_function_calls

# Find all authenticate() calls
results = find_function_calls("my-repo", "authenticate")

# Find TODO comments in Python
results = regex_search("my-repo", "TODO", language="python")

# Find imports in auth.py
results = regex_search("my-repo", "import", file_path="auth.py")
```

---

### 3. Read File (`read_file.py`)

Reconstruct complete files from chunks.

**Functions:**
- `read_file()` - Retrieve and reconstruct file contents
- `list_files()` - List all files in collection

**Use Cases:**
- View complete file from vector DB
- Export reconstructed source files
- Verify chunk coverage

**Example:**
```python
from src.tools import read_file, list_files

# Get complete file
result = read_file("my-repo", "src/auth.py")
print(result['content'])  # Full file content

# Get chunks without joining
result = read_file("my-repo", "auth.py", join_chunks=False)

# List all Python files
files = list_files("my-repo", language="python")
```

---

### 4. Semantic Search (`semantic_search.py`)

Natural language code search using embeddings and **cosine similarity**.

**Functions:**
- `semantic_search()` - Find semantically similar code
- `semantic_search_with_context()` - Search with additional context

**Use Cases:**
- "How is authentication handled?"
- "Find database connection logic"
- "Show error handling patterns"

**Example:**
```python
from src.tools import semantic_search, semantic_search_with_context

# Find authentication logic
results = semantic_search("my-repo", "How is authentication handled?")

# Find error handling in Python
results = semantic_search(
    "my-repo", 
    "error handling patterns", 
    language="python",
    n_results=10
)

# Search with context
result = semantic_search_with_context(
    "my-repo",
    "database connection",
    file_path="db.py"
)
print(result['context'])  # Files, languages, node types
```

**Cosine Similarity:**
- Returns scores between 0 and 1
- Higher score = more similar
- Uses OpenAI embeddings (text-embedding-3-large)

---

### 5. Full Text Search (`full_text_search.py`)

Advanced multi-criteria search with complex filters.

**Functions:**
- `full_text_search()` - Flexible metadata filtering
- `hybrid_search()` - Semantic + metadata filtering
- `search_by_type()` - Search by node type

**Use Cases:**
- Complex queries with multiple filters
- Combine semantic and metadata search
- Find all chunks of specific type

**Example:**
```python
from src.tools import full_text_search, hybrid_search, search_by_type

# Find all imports in auth.ts
results = full_text_search(
    "my-repo",
    text_pattern="import",
    where={"file_path": {"$contains": "auth.ts"}}
)

# Get all Python functions in utils/
results = full_text_search(
    "my-repo",
    where={
        "$and": [
            {"language": "python"},
            {"node_type": "function_definition"},
            {"file_path": {"$contains": "utils/"}}
        ]
    }
)

# Hybrid semantic + metadata search
results = hybrid_search(
    "my-repo",
    semantic_query="authentication and authorization",
    metadata_filters={"language": "python"}
)

# Get all Python classes
results = search_by_type("my-repo", "class_definition", language="python")
```

---

## 📊 Result Format

All tools return results in a consistent format:

```python
[
    {
        'id': 'chunk_123_456',
        'content': 'def authenticate():\n    ...',
        'metadata': {
            'file_path': '/path/to/file.py',
            'language': 'python',
            'node_type': 'function_definition',
            'node_name': 'authenticate',
            'start_line': 10,
            'end_line': 15,
            'hash': 'abc123...'
        },
        # For semantic/hybrid search only:
        'distance': 0.15,
        'cosine_similarity': 0.85
    }
]
```

---

## 🎯 ChromaDB Query Operators

### Metadata Filters (`where` clause)

```python
# Exact match
{"language": "python"}

# Contains (substring)
{"file_path": {"$contains": "auth"}}

# Comparison
{"start_line": {"$gt": 100}}

# Logical operators
{
    "$and": [
        {"language": "python"},
        {"node_type": "function_definition"}
    ]
}

{
    "$or": [
        {"language": "python"},
        {"language": "javascript"}
    ]
}
```

**Available Operators:**
- `$eq` - Equal
- `$ne` - Not equal
- `$gt` - Greater than
- `$gte` - Greater than or equal
- `$lt` - Less than
- `$lte` - Less than or equal
- `$in` - In list
- `$nin` - Not in list
- `$contains` - Substring match
- `$and` - Logical AND
- `$or` - Logical OR

---

## 🚀 Quick Start

```python
# Import tools
from src.tools import (
    symbol_search,
    regex_search,
    read_file,
    semantic_search,
    full_text_search
)

# 1. Find a class
results = symbol_search("my-repo", "UserController")

# 2. Find function calls
results = regex_search("my-repo", "authenticate(")

# 3. Read complete file
file_data = read_file("my-repo", "auth.py")

# 4. Semantic search
results = semantic_search("my-repo", "How does login work?")

# 5. Advanced search
results = full_text_search(
    "my-repo",
    where={"language": "python", "node_type": "class_definition"}
)
```

---

## 💡 Tips

1. **Use semantic search** for conceptual queries ("how does X work?")
2. **Use symbol search** for exact names (class/function names)
3. **Use regex search** for patterns (function calls, comments)
4. **Combine filters** for precise results
5. **Check cosine_similarity** scores - higher is better (0-1 range)

---

## 🔗 Integration

All tools connect to ChromaDB using the same pattern as `viewer.py`:
- HTTP server mode (default): `localhost:8000`
- Local persistence fallback
- Configurable via `.env` file
