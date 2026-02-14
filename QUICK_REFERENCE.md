# Contextinator v2.0 - Quick Reference

## Installation

```bash
# 1. Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. Build
./build.sh

# 3. Test
python test_v2.py
```

## Python API

```python
from contextinator import fs_read

# Line Mode - Read file with line ranges
result = fs_read("file.py", mode="Line", start_line=10, end_line=50)
result = fs_read("file.py", mode="Line", start_line=-10, end_line=-1)  # Last 10 lines

# Directory Mode - List files
result = fs_read("src/", mode="Directory", depth=0)  # Non-recursive
result = fs_read("src/", mode="Directory", depth=2)  # Recursive

# Search Mode - Pattern matching
result = fs_read("src/", mode="Search", pattern="TODO", context_lines=2)

# Batch Operations
results = fs_read(operations=[
    {"path": "file1.py", "mode": "Line"},
    {"path": "src/", "mode": "Search", "pattern": "TODO"}
])
```

## CLI

```bash
# Line Mode
contextinator read --path file.py --mode Line --start-line 10 --end-line 50
contextinator read --path file.py --mode Line --start-line -10 --end-line -1

# Directory Mode
contextinator read --path src/ --mode Directory --depth 2

# Search Mode
contextinator read --path src/ --mode Search --pattern "TODO" --context-lines 2

# JSON Output
contextinator read --path file.py --mode Line --format json
```

## Return Types

### Line Mode
```python
{
    "type": "line",
    "content": "file contents...",
    "total_lines": 100,
    "lines_returned": 10
}
```

### Directory Mode
```python
{
    "type": "directory",
    "entries": [
        {
            "path": "main.py",
            "is_dir": False,
            "size": 1024,
            "modified": 1234567890
        }
    ],
    "total_count": 10
}
```

### Search Mode
```python
{
    "type": "search",
    "matches": [
        {
            "file_path": "src/auth.py",
            "line_number": 42,
            "line_content": "TODO: implement",
            "context_before": ["line 40", "line 41"],
            "context_after": ["line 43", "line 44"]
        }
    ],
    "total_matches": 5
}
```

## File Structure

```
contextinator/
├── core/                    # Rust core
│   ├── src/
│   │   ├── lib.rs          # PyO3 bindings
│   │   ├── types.rs        # Core types
│   │   ├── line.rs         # Line mode
│   │   ├── directory.rs    # Directory mode
│   │   └── search.rs       # Search mode
│   └── Cargo.toml
├── src/contextinator/       # Python package
│   ├── __init__.py         # Exports fs_read
│   ├── tools.py            # Python wrapper
│   └── cli.py              # CLI
├── build.sh                # Build script
├── test_v2.py              # Tests
└── README_V2.md            # Documentation
```

## Common Patterns

### Read specific function
```python
# Find function line number first
search_result = fs_read("src/", mode="Search", pattern="def authenticate")
match = search_result["matches"][0]

# Read function (assume 20 lines)
func_result = fs_read(
    match["file_path"],
    mode="Line",
    start_line=match["line_number"] - 1,
    end_line=match["line_number"] + 20
)
```

### Find all TODOs
```python
result = fs_read(".", mode="Search", pattern="TODO|FIXME")
for match in result["matches"]:
    print(f"{match['file_path']}:{match['line_number']}: {match['line_content']}")
```

### Analyze directory structure
```python
result = fs_read(".", mode="Directory", depth=3)
files = [e for e in result["entries"] if not e["is_dir"]]
total_size = sum(f["size"] for f in files)
print(f"Total files: {len(files)}, Total size: {total_size} bytes")
```

## Performance

- File read: <1ms (files <100KB)
- Directory list: <10ms (dirs <1000 files)
- Pattern search: <100ms (repos <1M LOC)
- Memory: <10MB baseline

## Troubleshooting

### Rust not found
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### Build fails
```bash
# Clean and rebuild
cd core && cargo clean && cd ..
rm -rf target/
./build.sh
```

### Import error
```bash
# Make sure you built with maturin
maturin develop --release

# Or install in development mode
pip install -e .
```

## Next Steps

1. ✅ Build and test v2.0 core
2. 🔄 Add server mode (multi-repo support)
3. 🔄 Migrate v1 RAG to `contextinator.rag`
4. 🔄 Add optimizations (caching, streaming)
