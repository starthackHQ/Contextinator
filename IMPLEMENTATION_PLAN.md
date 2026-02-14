# Contextinator v2.0 Implementation Plan

## Executive Summary

Transform Contextinator from RAG-first to **filesystem-tools-first** architecture:
- **Primary**: Real-time filesystem tools (fs_read) for AI agents
- **Secondary**: Existing RAG pipeline (moved to `contextinator.rag` module)
- **Target**: Single server handling 100+ repos with <50ms latency

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Contextinator v2.0                          │
├─────────────────────────────────────────────────────────────┤
│  PRIMARY: Filesystem Tools (Rust Core)                      │
│  - fs_read (Line/Directory/Search modes)                    │
│  - Zero setup, instant access                               │
│  - <50ms response time                                       │
├─────────────────────────────────────────────────────────────┤
│  SECONDARY: RAG Module (Python, existing v1)                │
│  - contextinator.rag.chunk                                  │
│  - contextinator.rag.embed                                  │
│  - contextinator.rag.search                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase Breakdown

### **Phase 1: Rust Core Library** (Week 1-2)
**Goal**: Build high-performance filesystem tools in Rust

#### 1.1 Project Setup
- [ ] Create `core/` directory with Cargo.toml
- [ ] Setup Rust workspace structure
- [ ] Configure PyO3 for Python bindings
- [ ] Setup CI/CD for Rust builds

#### 1.2 Core Implementations
- [ ] **fs_read Line Mode**
  - Read file with line ranges (start_line, end_line)
  - Support negative indexing (-10 = last 10 lines)
  - Memory-mapped I/O for large files
  - UTF-8 validation and error handling
  
- [ ] **fs_read Directory Mode**
  - Recursive directory traversal (depth parameter)
  - Respect .gitignore patterns
  - Return file metadata (size, modified time)
  - Filter by file extensions
  
- [ ] **fs_read Search Mode**
  - Pattern matching with regex support
  - Context lines (before/after matches)
  - Multi-file concurrent search
  - Streaming results (don't buffer all)

- [ ] **Batch Operations**
  - Execute multiple operations in one call
  - Parallel execution with tokio
  - Aggregate results with error handling

#### 1.3 Performance Optimizations
- [ ] File descriptor pooling (LRU cache)
- [ ] Memory-mapped file reading
- [ ] Streaming response generation
- [ ] Request deduplication
- [ ] Benchmark suite (target: <50ms p95)

#### 1.4 Security
- [ ] Path traversal prevention
- [ ] Workspace boundary enforcement
- [ ] Symlink validation
- [ ] File size limits

**Deliverables**:
- `core/src/lib.rs` - Main library
- `core/src/fs_read.rs` - fs_read implementations
- `core/src/search.rs` - Pattern search engine
- `core/benches/` - Performance benchmarks
- Performance report showing <50ms p95

---

### **Phase 2: Python Bindings** (Week 2-3)
**Goal**: Expose Rust core to Python with clean API

#### 2.1 PyO3 Bindings
- [ ] Create Python module wrapper
- [ ] Implement fs_read function matching Amazon Q CLI signature
- [ ] Type hints and docstrings
- [ ] Error handling (Rust errors → Python exceptions)

#### 2.2 Python API Design
```python
from contextinator import fs_read

# Line mode
content = fs_read(
    path="src/main.py",
    mode="Line",
    start_line=10,
    end_line=50
)

# Directory mode
files = fs_read(
    path="src/",
    mode="Directory",
    depth=2
)

# Search mode
matches = fs_read(
    path="src/",
    mode="Search",
    pattern="def authenticate",
    context_lines=2
)

# Batch operations
results = fs_read(
    operations=[
        {"mode": "Line", "path": "file1.py"},
        {"mode": "Search", "path": "src/", "pattern": "TODO"}
    ]
)
```

#### 2.3 Async Support
- [ ] Async wrapper for concurrent operations
- [ ] Integration with asyncio
- [ ] Streaming results via async generators

**Deliverables**:
- `src/contextinator/tools.py` - Python API
- `src/contextinator/__init__.py` - Export fs_read as primary
- Type stubs (`.pyi` files)
- Unit tests for Python bindings

---

### **Phase 3: CLI Redesign** (Week 3-4)
**Goal**: New CLI with tools as primary interface

#### 3.1 New Command Structure
```bash
# Primary commands (v2)
contextinator read --mode Line --path src/main.py
contextinator read --mode Directory --path src/ --depth 2
contextinator read --mode Search --path src/ --pattern "TODO"
contextinator serve --workspaces /data/repos --port 8080

# Secondary commands (v1, preserved)
contextinator rag chunk --path /repo
contextinator rag embed --path /repo
contextinator rag search "query" --collection MyRepo
```

#### 3.2 CLI Implementation
- [ ] Refactor `cli.py` to support new command structure
- [ ] Add `read` command with mode subcommands
- [ ] Add `serve` command for server mode
- [ ] Move existing commands under `rag` namespace
- [ ] JSON and text output formatters
- [ ] Batch operations from JSON file

#### 3.3 Server Mode
- [ ] HTTP server with workspace routing
- [ ] POST /tool endpoint
- [ ] Workspace validation and isolation
- [ ] Concurrent request handling
- [ ] Health check endpoint

**Deliverables**:
- Updated `src/contextinator/cli.py`
- `src/contextinator/server.py` - HTTP server
- CLI help documentation
- Server deployment guide

---

### **Phase 4: v1 → RAG Module Migration** (Week 4)
**Goal**: Move existing codebase to `contextinator.rag` without breaking changes

#### 4.1 Directory Restructuring
```
src/contextinator/
├── __init__.py          # NEW: Exports fs_read as primary
├── tools.py             # NEW: Tool implementations
├── cli.py               # UPDATED: New primary commands
├── server.py            # NEW: Multi-repo server
└── rag/                 # MOVED: All v1 code
    ├── __init__.py
    ├── chunking/
    ├── embedding/
    ├── ingestion/
    ├── vectorstore/
    ├── config/
    ├── utils/
    └── cli.py           # v1 CLI commands
```

#### 4.2 Import Updates
- [ ] Move all v1 modules to `contextinator.rag/`
- [ ] Update internal imports within RAG module
- [ ] Create `contextinator.rag.__init__.py` with exports
- [ ] Add deprecation warnings for old imports
- [ ] Backward compatibility shims

#### 4.3 CLI Namespace Migration
- [ ] Prefix all v1 commands with `rag`
- [ ] `chunk` → `rag chunk`
- [ ] `embed` → `rag embed`
- [ ] `search` → `rag search`
- [ ] Keep old commands with deprecation warnings

**Deliverables**:
- Restructured directory with `rag/` module
- Migration script for existing users
- Backward compatibility tests
- Updated imports throughout codebase

---

### **Phase 5: Documentation & Testing** (Week 5)
**Goal**: Comprehensive docs and test coverage

#### 5.1 Documentation
- [ ] **README.md** - Showcase v2 as primary
  - Quick start with fs_read
  - Server mode setup
  - "Advanced: RAG Module" section
  
- [ ] **USAGE.md** - Tool reference
  - fs_read modes with examples
  - Server API documentation
  - Performance characteristics
  
- [ ] **RAG_MODULE.md** - v1 documentation
  - Chunking, embedding, search
  - Migration from v1 to v2
  
- [ ] **API_REFERENCE.md** - Python API docs
  - Function signatures
  - Type hints
  - Usage examples

#### 5.2 Testing
- [ ] Rust unit tests (core library)
- [ ] Rust integration tests
- [ ] Python unit tests (bindings)
- [ ] Python integration tests
- [ ] CLI end-to-end tests
- [ ] Server load tests (100 concurrent requests)
- [ ] Performance regression tests

#### 5.3 Examples
- [ ] Basic tool usage examples
- [ ] Server deployment examples
- [ ] RAG module examples
- [ ] AI agent integration examples

**Deliverables**:
- Complete documentation suite
- 80%+ test coverage
- Example repository
- Performance benchmarks

---

## Technical Specifications

### Rust Core API

```rust
// core/src/lib.rs
pub enum FsReadMode {
    Line { start_line: Option<i32>, end_line: Option<i32> },
    Directory { depth: u32 },
    Search { pattern: String, context_lines: u32 },
}

pub struct FsReadParams {
    pub path: PathBuf,
    pub mode: FsReadMode,
}

pub async fn fs_read(params: FsReadParams) -> Result<FsReadResult>;
pub async fn fs_read_batch(operations: Vec<FsReadParams>) -> Vec<Result<FsReadResult>>;
```

### Python API

```python
# src/contextinator/__init__.py
from .tools import fs_read

__all__ = ["fs_read"]

# src/contextinator/tools.py
def fs_read(
    path: str,
    mode: Literal["Line", "Directory", "Search"],
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    depth: int = 0,
    pattern: Optional[str] = None,
    context_lines: int = 2,
    operations: Optional[List[Dict]] = None,
) -> Union[str, List[Dict], List[Any]]:
    """
    Read filesystem with multiple modes.
    
    Matches Amazon Q CLI fs_read tool signature.
    """
    pass
```

### Server API

```
POST /tool
Content-Type: application/json

{
  "workspace": "repo-001",
  "tool": "fs_read",
  "params": {
    "mode": "Line",
    "path": "src/main.py",
    "start_line": 10,
    "end_line": 50
  }
}

Response:
{
  "success": true,
  "result": "...",
  "latency_ms": 12
}
```

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| File read (<100KB) | <1ms | p95 latency |
| Directory listing (<1000 files) | <10ms | p95 latency |
| Pattern search (<1M LOC) | <100ms | p95 latency |
| Memory (baseline) | <10MB | Single repo |
| Memory (100 repos) | <200MB | Server mode |
| Throughput | 1000 req/s | Server mode |
| CPU (peak) | <30% | Server mode |

---

## Migration Strategy

### For Existing Users

**Option 1: Keep using v1 (RAG)**
```bash
# Old commands still work with 'rag' prefix
contextinator rag chunk --path /repo
contextinator rag embed --path /repo
contextinator rag search "query" -c MyRepo
```

**Option 2: Adopt v2 (Tools)**
```bash
# New instant filesystem tools
contextinator read --mode Search --path /repo --pattern "TODO"
```

**Option 3: Hybrid**
```python
# Use tools for quick access
from contextinator import fs_read
content = fs_read(path="src/main.py", mode="Line")

# Use RAG for semantic search
from contextinator.rag import semantic_search
results = semantic_search("authentication logic", collection="MyRepo")
```

### Breaking Changes
- None! All v1 functionality preserved under `contextinator.rag`
- CLI commands namespaced: `contextinator rag <command>`
- Imports updated: `from contextinator.rag import ...`

---

## Success Criteria

### Must Have
- ✅ fs_read tool with Line/Directory/Search modes
- ✅ <50ms p95 latency for all operations
- ✅ Server mode handling 100+ concurrent repos
- ✅ 100% backward compatibility for v1 users
- ✅ Zero setup for basic tool usage

### Nice to Have
- 🎯 Rust CLI binary (no Python dependency)
- 🎯 WebSocket streaming for large results
- 🎯 File watching for live updates
- 🎯 Distributed server mode (multiple nodes)

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Rust learning curve | High | Start with simple implementations, iterate |
| PyO3 binding complexity | Medium | Use maturin for build automation |
| Breaking existing users | High | Preserve v1 under `rag` namespace |
| Performance targets not met | Medium | Benchmark early, optimize incrementally |
| Server security issues | High | Path validation, workspace isolation |

---

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Rust Core | 2 weeks | None |
| Phase 2: Python Bindings | 1 week | Phase 1 |
| Phase 3: CLI Redesign | 1 week | Phase 2 |
| Phase 4: RAG Migration | 1 week | Phase 3 |
| Phase 5: Docs & Testing | 1 week | Phase 4 |
| **Total** | **6 weeks** | |

---

## Next Steps

1. **Review & Approve Plan** - Team alignment on architecture
2. **Setup Rust Environment** - Install toolchain, configure workspace
3. **Prototype fs_read Line Mode** - Validate approach with simplest mode
4. **Benchmark Prototype** - Ensure performance targets are achievable
5. **Iterate** - Build remaining modes, optimize, test

---

## Open Questions

1. **Rust vs Python for server?** 
   - Rust: Better performance, harder to maintain
   - Python: Easier development, good enough performance with async

2. **Authentication for server mode?**
   - API keys per workspace?
   - OAuth integration?
   - None (internal network only)?

3. **Rate limiting strategy?**
   - Per workspace?
   - Global?
   - None?

4. **Monitoring & observability?**
   - Prometheus metrics?
   - Structured logging?
   - Tracing?

5. **Deployment model?**
   - Docker container?
   - Systemd service?
   - Kubernetes?

---

## Appendix: Tool Signature Reference

### Amazon Q CLI fs_read Tool

```typescript
interface FsReadOperation {
  mode: "Line" | "Directory" | "Search";
  path: string;
  
  // Line mode
  start_line?: number;  // Negative for lines from end
  end_line?: number;    // Negative for lines from end
  
  // Directory mode
  depth?: number;       // 0 = non-recursive
  
  // Search mode
  pattern?: string;
  context_lines?: number;  // Default: 2
}

interface FsReadBatch {
  operations: FsReadOperation[];
}

function fs_read(params: FsReadOperation | FsReadBatch): Result;
```

**Our implementation must match this signature exactly for compatibility.**
