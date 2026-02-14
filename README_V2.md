# Contextinator v2.0

**Filesystem tools for AI agents with optional RAG capabilities**

## What's New in v2.0

Contextinator v2.0 is a complete architectural redesign:

- **Primary**: Zero-setup filesystem tools (`fs_read`) for instant code access
- **Secondary**: Optional RAG module for semantic search (v1 functionality)
- **Performance**: Rust-powered core with <50ms response times
- **Simplicity**: No databases, no embeddings, no setup required

## Quick Start

### Installation

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Clone and build
git clone https://github.com/starthackHQ/Contextinator.git
cd Contextinator
./build.sh

# Or install from PyPI (coming soon)
pip install contextinator
```

### Basic Usage

```bash
# Read file lines 10-50
contextinator read --path src/main.py --mode Line --start-line 10 --end-line 50

# Read last 10 lines
contextinator read --path src/main.py --mode Line --start-line -10 --end-line -1

# List directory (depth 2)
contextinator read --path src/ --mode Directory --depth 2

# Search for pattern
contextinator read --path src/ --mode Search --pattern "def authenticate"

# JSON output
contextinator read --path src/main.py --mode Line --format json
```

### Python API

```python
from contextinator import fs_read

# Read file
result = fs_read("src/main.py", mode="Line", start_line=10, end_line=50)
print(result["content"])

# List directory
result = fs_read("src/", mode="Directory", depth=2)
for entry in result["entries"]:
    print(f"{entry['path']} - {entry['size']} bytes")

# Search pattern
result = fs_read("src/", mode="Search", pattern="TODO")
for match in result["matches"]:
    print(f"{match['file_path']}:{match['line_number']}: {match['line_content']}")

# Batch operations
results = fs_read(operations=[
    {"path": "file1.py", "mode": "Line"},
    {"path": "src/", "mode": "Search", "pattern": "TODO"}
])
```

## Tool Modes

### Line Mode

Read file contents with optional line ranges. Supports negative indexing.

```python
# Read entire file
fs_read("file.py", mode="Line")

# Read lines 10-50
fs_read("file.py", mode="Line", start_line=10, end_line=50)

# Read last 10 lines
fs_read("file.py", mode="Line", start_line=-10, end_line=-1)
```

**Returns:**
```json
{
  "type": "line",
  "content": "...",
  "total_lines": 100,
  "lines_returned": 10
}
```

### Directory Mode

List directory contents recursively.

```python
# Non-recursive (depth=0)
fs_read("src/", mode="Directory", depth=0)

# Recursive (depth=2)
fs_read("src/", mode="Directory", depth=2)
```

**Returns:**
```json
{
  "type": "directory",
  "entries": [
    {
      "path": "main.py",
      "is_dir": false,
      "size": 1024,
      "modified": 1234567890
    }
  ],
  "total_count": 10
}
```

### Search Mode

Search for patterns with context lines.

```python
# Search with default context (2 lines)
fs_read("src/", mode="Search", pattern="TODO")

# Search with custom context
fs_read("src/", mode="Search", pattern="def.*auth", context_lines=5)
```

**Returns:**
```json
{
  "type": "search",
  "matches": [
    {
      "file_path": "src/auth.py",
      "line_number": 42,
      "line_content": "TODO: implement auth",
      "context_before": ["...", "..."],
      "context_after": ["...", "..."]
    }
  ],
  "total_matches": 5
}
```

## Performance

Built in Rust for maximum speed:

- **File read**: <1ms for files under 100KB
- **Directory listing**: <10ms for directories with <1000 files
- **Pattern search**: <100ms for repositories under 1M LOC
- **Memory**: <10MB baseline

## Architecture

```
┌─────────────────────────────────────┐
│     Python API (contextinator)      │
├─────────────────────────────────────┤
│     PyO3 Bindings                   │
├─────────────────────────────────────┤
│     Rust Core (contextinator-core)  │
│     • Line Mode                     │
│     • Directory Mode                │
│     • Search Mode                   │
└─────────────────────────────────────┘
```

## Advanced: RAG Module (Optional)

For semantic search and code intelligence, use the optional RAG module:

```bash
# Install RAG dependencies
pip install contextinator[rag]

# Use RAG features (v1 functionality)
# Coming soon: contextinator rag chunk --path /repo
```

## Development

### Build from Source

```bash
# Install dependencies
pip install maturin

# Build Rust core
cd core
cargo build --release

# Build Python package
maturin develop --release

# Run tests
cargo test
pytest
```

### Project Structure

```
contextinator/
├── core/                 # Rust core library
│   ├── src/
│   │   ├── lib.rs       # PyO3 bindings
│   │   ├── types.rs     # Core types
│   │   ├── line.rs      # Line mode
│   │   ├── directory.rs # Directory mode
│   │   └── search.rs    # Search mode
│   └── Cargo.toml
├── src/contextinator/    # Python package
│   ├── __init__.py      # Exports fs_read
│   ├── tools.py         # Python wrapper
│   └── cli.py           # CLI interface
└── pyproject.toml       # Package config
```

## Comparison: v1 vs v2

| Feature | v1 (RAG-first) | v2 (Tools-first) |
|---------|----------------|------------------|
| Setup time | Minutes (ingestion) | Zero |
| Dependencies | ChromaDB, OpenAI | None (Rust only) |
| Storage | Vector DB required | None |
| Speed | Seconds (embedding) | Milliseconds |
| Use case | Semantic search | Direct file access |
| Best for | AI reasoning | AI tool calls |

## Use Cases

### AI Agent Tool Calls

```python
# Agent needs to read a file
def read_file_tool(path: str, start: int, end: int):
    return fs_read(path, mode="Line", start_line=start, end_line=end)

# Agent needs to search code
def search_code_tool(path: str, pattern: str):
    return fs_read(path, mode="Search", pattern=pattern)
```

### Code Analysis

```python
# Find all TODOs in codebase
result = fs_read(".", mode="Search", pattern="TODO|FIXME")
todos = result["matches"]

# Analyze directory structure
result = fs_read(".", mode="Directory", depth=3)
files = [e for e in result["entries"] if not e["is_dir"]]
```

### File Inspection

```python
# Read function definition
result = fs_read("src/auth.py", mode="Line", start_line=42, end_line=60)

# Check last 20 lines of log
result = fs_read("app.log", mode="Line", start_line=-20, end_line=-1)
```

## License

Apache-2.0

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

## Acknowledgements

- Inspired by Amazon Q CLI's filesystem tools
- Built with [PyO3](https://pyo3.rs/) and [Rust](https://www.rust-lang.org/)
