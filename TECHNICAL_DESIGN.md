# Contextinator v2.0 Technical Design

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Agent / User                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
    ┌────▼─────┐                   ┌────▼─────┐
    │ CLI Mode │                   │  Server  │
    │          │                   │   Mode   │
    └────┬─────┘                   └────┬─────┘
         │                               │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │   Python API Layer            │
         │   (contextinator.tools)       │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │   PyO3 Bindings               │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │   Rust Core Library           │
         │   (contextinator-core)        │
         │                               │
         │  ┌─────────────────────────┐  │
         │  │ fs_read Engine          │  │
         │  ├─────────────────────────┤  │
         │  │ • Line Mode             │  │
         │  │ • Directory Mode        │  │
         │  │ • Search Mode           │  │
         │  │ • Batch Operations      │  │
         │  └─────────────────────────┘  │
         │                               │
         │  ┌─────────────────────────┐  │
         │  │ Optimizations           │  │
         │  ├─────────────────────────┤  │
         │  │ • File Descriptor Pool  │  │
         │  │ • Memory-Mapped I/O     │  │
         │  │ • Request Dedup         │  │
         │  │ • Streaming Results     │  │
         │  └─────────────────────────┘  │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │   Filesystem                  │
         │   (Local Repositories)        │
         └───────────────────────────────┘
```

---

## Component Design

### 1. Rust Core Library (`core/`)

#### 1.1 Module Structure

```
core/
├── Cargo.toml
├── src/
│   ├── lib.rs              # Public API, PyO3 exports
│   ├── fs_read/
│   │   ├── mod.rs          # Main fs_read dispatcher
│   │   ├── line.rs         # Line mode implementation
│   │   ├── directory.rs    # Directory mode implementation
│   │   └── search.rs       # Search mode implementation
│   ├── optimizations/
│   │   ├── mod.rs
│   │   ├── file_cache.rs   # File descriptor pooling
│   │   ├── mmap.rs         # Memory-mapped I/O
│   │   └── dedup.rs        # Request deduplication
│   ├── security/
│   │   ├── mod.rs
│   │   ├── path_validator.rs
│   │   └── workspace.rs    # Workspace isolation
│   └── types.rs            # Shared types and structs
└── benches/
    └── fs_read_bench.rs    # Performance benchmarks
```

#### 1.2 Core Types

```rust
// core/src/types.rs

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FsReadMode {
    Line {
        start_line: Option<i32>,
        end_line: Option<i32>,
    },
    Directory {
        depth: u32,
    },
    Search {
        pattern: String,
        context_lines: u32,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FsReadParams {
    pub path: PathBuf,
    pub mode: FsReadMode,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FsReadBatchParams {
    pub operations: Vec<FsReadParams>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum FsReadResult {
    Line {
        content: String,
        total_lines: usize,
        lines_returned: usize,
    },
    Directory {
        entries: Vec<FileEntry>,
        total_count: usize,
    },
    Search {
        matches: Vec<SearchMatch>,
        total_matches: usize,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileEntry {
    pub path: PathBuf,
    pub is_dir: bool,
    pub size: u64,
    pub modified: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchMatch {
    pub file_path: PathBuf,
    pub line_number: usize,
    pub line_content: String,
    pub context_before: Vec<String>,
    pub context_after: Vec<String>,
}

#[derive(Debug)]
pub enum FsReadError {
    PathNotFound(PathBuf),
    PermissionDenied(PathBuf),
    InvalidPath(String),
    IoError(std::io::Error),
    InvalidLineRange(i32, i32),
}
```

#### 1.3 Line Mode Implementation

```rust
// core/src/fs_read/line.rs

use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;
use memmap2::Mmap;

pub struct LineReader {
    file_cache: Arc<FileCache>,
}

impl LineReader {
    pub async fn read_lines(
        &self,
        path: &Path,
        start_line: Option<i32>,
        end_line: Option<i32>,
    ) -> Result<FsReadResult, FsReadError> {
        // Validate path
        if !path.exists() {
            return Err(FsReadError::PathNotFound(path.to_path_buf()));
        }

        // Get file metadata
        let metadata = std::fs::metadata(path)?;
        let file_size = metadata.len();

        // Choose strategy based on file size
        if file_size > 10_000_000 {
            // Large file: use memory-mapped I/O
            self.read_lines_mmap(path, start_line, end_line).await
        } else {
            // Small file: use buffered reader
            self.read_lines_buffered(path, start_line, end_line).await
        }
    }

    async fn read_lines_buffered(
        &self,
        path: &Path,
        start_line: Option<i32>,
        end_line: Option<i32>,
    ) -> Result<FsReadResult, FsReadError> {
        let file = File::open(path)?;
        let reader = BufReader::new(file);
        let lines: Vec<String> = reader.lines().collect::<Result<_, _>>()?;
        
        let total_lines = lines.len();
        let (start, end) = self.resolve_line_range(start_line, end_line, total_lines)?;
        
        let selected_lines: Vec<String> = lines[start..end].to_vec();
        let content = selected_lines.join("\n");

        Ok(FsReadResult::Line {
            content,
            total_lines,
            lines_returned: selected_lines.len(),
        })
    }

    fn resolve_line_range(
        &self,
        start: Option<i32>,
        end: Option<i32>,
        total_lines: usize,
    ) -> Result<(usize, usize), FsReadError> {
        let start_idx = match start {
            None => 0,
            Some(n) if n >= 0 => n as usize,
            Some(n) => {
                // Negative indexing: -1 = last line
                let abs = n.abs() as usize;
                if abs > total_lines {
                    0
                } else {
                    total_lines - abs
                }
            }
        };

        let end_idx = match end {
            None => total_lines,
            Some(n) if n >= 0 => (n as usize).min(total_lines),
            Some(n) => {
                let abs = n.abs() as usize;
                if abs > total_lines {
                    0
                } else {
                    total_lines - abs + 1
                }
            }
        };

        if start_idx > end_idx {
            return Err(FsReadError::InvalidLineRange(
                start.unwrap_or(0),
                end.unwrap_or(0),
            ));
        }

        Ok((start_idx, end_idx))
    }
}
```

#### 1.4 Directory Mode Implementation

```rust
// core/src/fs_read/directory.rs

use walkdir::WalkDir;
use std::path::Path;

pub struct DirectoryReader {
    ignore_patterns: Vec<String>,
}

impl DirectoryReader {
    pub async fn list_directory(
        &self,
        path: &Path,
        depth: u32,
    ) -> Result<FsReadResult, FsReadError> {
        let mut entries = Vec::new();

        let walker = if depth == 0 {
            WalkDir::new(path).max_depth(1)
        } else {
            WalkDir::new(path).max_depth(depth as usize)
        };

        for entry in walker.into_iter().filter_entry(|e| self.should_include(e)) {
            let entry = entry?;
            let metadata = entry.metadata()?;

            entries.push(FileEntry {
                path: entry.path().to_path_buf(),
                is_dir: metadata.is_dir(),
                size: metadata.len(),
                modified: metadata.modified().ok().map(|t| {
                    t.duration_since(std::time::UNIX_EPOCH)
                        .unwrap()
                        .as_secs()
                }),
            });
        }

        Ok(FsReadResult::Directory {
            total_count: entries.len(),
            entries,
        })
    }

    fn should_include(&self, entry: &walkdir::DirEntry) -> bool {
        // Skip hidden files and ignored patterns
        let name = entry.file_name().to_string_lossy();
        
        if name.starts_with('.') {
            return false;
        }

        for pattern in &self.ignore_patterns {
            if name.contains(pattern) {
                return false;
            }
        }

        true
    }
}
```

#### 1.5 Search Mode Implementation

```rust
// core/src/fs_read/search.rs

use regex::Regex;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;
use tokio::task;

pub struct SearchEngine {
    max_concurrent: usize,
}

impl SearchEngine {
    pub async fn search_pattern(
        &self,
        path: &Path,
        pattern: &str,
        context_lines: u32,
    ) -> Result<FsReadResult, FsReadError> {
        let regex = Regex::new(pattern)
            .map_err(|e| FsReadError::InvalidPattern(e.to_string()))?;

        let mut matches = Vec::new();

        if path.is_file() {
            // Search single file
            matches.extend(self.search_file(path, &regex, context_lines).await?);
        } else {
            // Search directory recursively
            matches.extend(self.search_directory(path, &regex, context_lines).await?);
        }

        Ok(FsReadResult::Search {
            total_matches: matches.len(),
            matches,
        })
    }

    async fn search_file(
        &self,
        path: &Path,
        regex: &Regex,
        context_lines: u32,
    ) -> Result<Vec<SearchMatch>, FsReadError> {
        let file = File::open(path)?;
        let reader = BufReader::new(file);
        let lines: Vec<String> = reader.lines().collect::<Result<_, _>>()?;

        let mut matches = Vec::new();

        for (line_num, line) in lines.iter().enumerate() {
            if regex.is_match(line) {
                let context_before = self.get_context_before(&lines, line_num, context_lines);
                let context_after = self.get_context_after(&lines, line_num, context_lines);

                matches.push(SearchMatch {
                    file_path: path.to_path_buf(),
                    line_number: line_num + 1,
                    line_content: line.clone(),
                    context_before,
                    context_after,
                });
            }
        }

        Ok(matches)
    }

    async fn search_directory(
        &self,
        path: &Path,
        regex: &Regex,
        context_lines: u32,
    ) -> Result<Vec<SearchMatch>, FsReadError> {
        let mut tasks = Vec::new();
        
        for entry in WalkDir::new(path).into_iter().filter_map(|e| e.ok()) {
            if entry.file_type().is_file() {
                let path = entry.path().to_path_buf();
                let regex = regex.clone();
                
                tasks.push(task::spawn(async move {
                    self.search_file(&path, &regex, context_lines).await
                }));
            }
        }

        let mut all_matches = Vec::new();
        for task in tasks {
            if let Ok(Ok(matches)) = task.await {
                all_matches.extend(matches);
            }
        }

        Ok(all_matches)
    }

    fn get_context_before(&self, lines: &[String], index: usize, count: u32) -> Vec<String> {
        let start = index.saturating_sub(count as usize);
        lines[start..index].to_vec()
    }

    fn get_context_after(&self, lines: &[String], index: usize, count: u32) -> Vec<String> {
        let end = (index + 1 + count as usize).min(lines.len());
        lines[index + 1..end].to_vec()
    }
}
```

---

### 2. Python Bindings Layer

#### 2.1 PyO3 Integration

```rust
// core/src/lib.rs

use pyo3::prelude::*;

#[pyfunction]
fn fs_read(
    py: Python,
    path: String,
    mode: String,
    start_line: Option<i32>,
    end_line: Option<i32>,
    depth: Option<u32>,
    pattern: Option<String>,
    context_lines: Option<u32>,
) -> PyResult<PyObject> {
    let params = parse_params(path, mode, start_line, end_line, depth, pattern, context_lines)?;
    
    let result = py.allow_threads(|| {
        tokio::runtime::Runtime::new()
            .unwrap()
            .block_on(async {
                fs_read_impl(params).await
            })
    })?;

    // Convert Rust result to Python dict
    Ok(result_to_python(py, result)?)
}

#[pyfunction]
fn fs_read_batch(py: Python, operations: Vec<PyObject>) -> PyResult<Vec<PyObject>> {
    // Parse operations from Python
    let params = parse_batch_params(operations)?;
    
    let results = py.allow_threads(|| {
        tokio::runtime::Runtime::new()
            .unwrap()
            .block_on(async {
                fs_read_batch_impl(params).await
            })
    })?;

    // Convert results to Python
    results.into_iter()
        .map(|r| result_to_python(py, r))
        .collect()
}

#[pymodule]
fn contextinator_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fs_read, m)?)?;
    m.add_function(wrap_pyfunction!(fs_read_batch, m)?)?;
    Ok(())
}
```

#### 2.2 Python Wrapper

```python
# src/contextinator/tools.py

from typing import Literal, Optional, List, Dict, Union, Any
import contextinator_core

def fs_read(
    path: str,
    mode: Literal["Line", "Directory", "Search"],
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    depth: int = 0,
    pattern: Optional[str] = None,
    context_lines: int = 2,
    operations: Optional[List[Dict[str, Any]]] = None,
) -> Union[str, List[Dict], Dict]:
    """
    Read filesystem with multiple modes.
    
    Matches Amazon Q CLI fs_read tool signature.
    
    Args:
        path: File or directory path
        mode: Operation mode (Line, Directory, Search)
        start_line: Starting line (negative for lines from end)
        end_line: Ending line (negative for lines from end)
        depth: Directory traversal depth (0 = non-recursive)
        pattern: Search pattern (regex)
        context_lines: Lines of context around matches
        operations: Batch operations list
        
    Returns:
        Result based on mode:
        - Line: String content
        - Directory: List of file entries
        - Search: List of matches
        
    Examples:
        >>> # Read lines 10-50
        >>> content = fs_read("src/main.py", mode="Line", start_line=10, end_line=50)
        
        >>> # Read last 10 lines
        >>> content = fs_read("src/main.py", mode="Line", start_line=-10, end_line=-1)
        
        >>> # List directory
        >>> files = fs_read("src/", mode="Directory", depth=2)
        
        >>> # Search pattern
        >>> matches = fs_read("src/", mode="Search", pattern="def authenticate")
        
        >>> # Batch operations
        >>> results = fs_read(operations=[
        ...     {"path": "file1.py", "mode": "Line"},
        ...     {"path": "src/", "mode": "Search", "pattern": "TODO"}
        ... ])
    """
    if operations:
        return contextinator_core.fs_read_batch(operations)
    
    return contextinator_core.fs_read(
        path=path,
        mode=mode,
        start_line=start_line,
        end_line=end_line,
        depth=depth,
        pattern=pattern,
        context_lines=context_lines,
    )
```

---

### 3. Server Mode Architecture

#### 3.1 Server Design

```python
# src/contextinator/server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
from pathlib import Path

app = FastAPI(title="Contextinator Server")

class ToolRequest(BaseModel):
    workspace: str
    tool: str
    params: Dict[str, Any]

class ToolResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    latency_ms: float

class WorkspaceRegistry:
    def __init__(self, workspaces_root: Path):
        self.root = workspaces_root
        self.workspaces: Dict[str, Path] = {}
        self._load_workspaces()
    
    def _load_workspaces(self):
        """Discover all workspace directories."""
        for workspace_dir in self.root.iterdir():
            if workspace_dir.is_dir():
                self.workspaces[workspace_dir.name] = workspace_dir
    
    def get_workspace_path(self, workspace_id: str) -> Path:
        """Get validated workspace path."""
        if workspace_id not in self.workspaces:
            raise ValueError(f"Unknown workspace: {workspace_id}")
        return self.workspaces[workspace_id]
    
    def validate_path(self, workspace_id: str, path: str) -> Path:
        """Validate path is within workspace bounds."""
        workspace_root = self.get_workspace_path(workspace_id)
        full_path = (workspace_root / path).resolve()
        
        # Prevent path traversal
        if not full_path.is_relative_to(workspace_root):
            raise ValueError(f"Path traversal detected: {path}")
        
        return full_path

# Global registry
registry: Optional[WorkspaceRegistry] = None

@app.on_event("startup")
async def startup():
    global registry
    workspaces_root = Path(os.getenv("WORKSPACES_ROOT", "/data/repos"))
    registry = WorkspaceRegistry(workspaces_root)

@app.post("/tool", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute tool call for specific workspace."""
    import time
    start = time.time()
    
    try:
        # Validate workspace
        workspace_path = registry.get_workspace_path(request.workspace)
        
        # Validate and resolve path
        if "path" in request.params:
            request.params["path"] = str(
                registry.validate_path(request.workspace, request.params["path"])
            )
        
        # Execute tool
        if request.tool == "fs_read":
            from contextinator import fs_read
            result = fs_read(**request.params)
        else:
            raise ValueError(f"Unknown tool: {request.tool}")
        
        latency = (time.time() - start) * 1000
        
        return ToolResponse(
            success=True,
            result=result,
            latency_ms=latency
        )
    
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ToolResponse(
            success=False,
            error=str(e),
            latency_ms=latency
        )

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "workspaces": len(registry.workspaces),
        "workspace_ids": list(registry.workspaces.keys())
    }

def serve(workspaces_root: str, port: int = 8080, max_concurrent: int = 200):
    """Start server."""
    import uvicorn
    
    os.environ["WORKSPACES_ROOT"] = workspaces_root
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        workers=1,
        limit_concurrency=max_concurrent
    )
```

---

## Performance Optimizations

### 1. File Descriptor Pooling

```rust
// core/src/optimizations/file_cache.rs

use lru::LruCache;
use std::fs::File;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

pub struct FileCache {
    cache: Arc<Mutex<LruCache<PathBuf, Arc<File>>>>,
}

impl FileCache {
    pub fn new(capacity: usize) -> Self {
        Self {
            cache: Arc::new(Mutex::new(LruCache::new(capacity))),
        }
    }

    pub fn get_or_open(&self, path: &PathBuf) -> Result<Arc<File>, std::io::Error> {
        let mut cache = self.cache.lock().unwrap();
        
        if let Some(file) = cache.get(path) {
            return Ok(Arc::clone(file));
        }

        let file = Arc::new(File::open(path)?);
        cache.put(path.clone(), Arc::clone(&file));
        Ok(file)
    }
}
```

### 2. Request Deduplication

```rust
// core/src/optimizations/dedup.rs

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tokio::sync::Notify;

pub struct RequestDeduplicator {
    in_flight: Arc<Mutex<HashMap<String, Arc<Notify>>>>,
    results: Arc<Mutex<HashMap<String, FsReadResult>>>,
}

impl RequestDeduplicator {
    pub async fn execute<F, Fut>(
        &self,
        key: String,
        f: F,
    ) -> Result<FsReadResult, FsReadError>
    where
        F: FnOnce() -> Fut,
        Fut: std::future::Future<Output = Result<FsReadResult, FsReadError>>,
    {
        // Check if request is in flight
        let notify = {
            let mut in_flight = self.in_flight.lock().unwrap();
            if let Some(notify) = in_flight.get(&key) {
                Arc::clone(notify)
            } else {
                let notify = Arc::new(Notify::new());
                in_flight.insert(key.clone(), Arc::clone(&notify));
                drop(in_flight);
                
                // Execute request
                let result = f().await?;
                
                // Store result
                self.results.lock().unwrap().insert(key.clone(), result.clone());
                
                // Notify waiters
                notify.notify_waiters();
                
                // Clean up
                self.in_flight.lock().unwrap().remove(&key);
                
                return Ok(result);
            }
        };

        // Wait for in-flight request
        notify.notified().await;
        
        // Get result
        Ok(self.results.lock().unwrap().get(&key).unwrap().clone())
    }
}
```

---

## Security Considerations

### 1. Path Validation

```rust
// core/src/security/path_validator.rs

use std::path::{Path, PathBuf};

pub struct PathValidator {
    allowed_roots: Vec<PathBuf>,
}

impl PathValidator {
    pub fn validate(&self, path: &Path) -> Result<PathBuf, SecurityError> {
        // Canonicalize path (resolve symlinks, .., etc.)
        let canonical = path.canonicalize()
            .map_err(|_| SecurityError::InvalidPath)?;

        // Check if path is within allowed roots
        for root in &self.allowed_roots {
            if canonical.starts_with(root) {
                return Ok(canonical);
            }
        }

        Err(SecurityError::PathTraversal)
    }
}
```

### 2. Workspace Isolation

```rust
// core/src/security/workspace.rs

pub struct Workspace {
    id: String,
    root: PathBuf,
    validator: PathValidator,
}

impl Workspace {
    pub fn resolve_path(&self, relative_path: &str) -> Result<PathBuf, SecurityError> {
        let full_path = self.root.join(relative_path);
        self.validator.validate(&full_path)
    }
}
```

---

## Testing Strategy

### 1. Unit Tests (Rust)
- Line mode with various ranges
- Negative indexing
- Directory traversal
- Pattern matching
- Error handling

### 2. Integration Tests (Python)
- Python bindings correctness
- Async operations
- Batch operations
- Error propagation

### 3. Performance Tests
- Benchmark suite with criterion
- Load testing server mode
- Memory profiling
- Latency measurements

### 4. Security Tests
- Path traversal attempts
- Symlink attacks
- Workspace boundary violations

---

## Deployment

### Docker Container

```dockerfile
FROM rust:1.75 as builder
WORKDIR /app
COPY core/ ./core/
RUN cd core && cargo build --release

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/core/target/release/libcontextinator_core.so /app/
COPY src/ ./src/
RUN pip install -e .

EXPOSE 8080
CMD ["contextinator", "serve", "--workspaces", "/data/repos", "--port", "8080"]
```

---

This technical design provides the foundation for implementing the v2.0 architecture. Ready to proceed with implementation?
