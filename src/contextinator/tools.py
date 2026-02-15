"""
Filesystem tools for AI agents.

Provides fs_read tool matching Amazon Q CLI specification.
"""

import json
from typing import Any, Dict, List, Literal, Optional, Union

try:
    from contextinator import contextinator_core
    HAS_RUST_CORE = True
except ImportError:
    HAS_RUST_CORE = False
    import warnings
    warnings.warn("Rust core not available, using Python fallback")


def fs_read(
    path: str,
    mode: Literal["Line", "Directory", "Search"],
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    depth: int = 0,
    pattern: Optional[str] = None,
    context_lines: int = 2,
    operations: Optional[List[Dict[str, Any]]] = None,
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
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
        - Line: {"type": "line", "content": str, "total_lines": int, "lines_returned": int}
        - Directory: {"type": "directory", "entries": [...], "total_count": int}
        - Search: {"type": "search", "matches": [...], "total_matches": int}
        
    Examples:
        >>> # Read lines 10-50
        >>> result = fs_read("src/main.py", mode="Line", start_line=10, end_line=50)
        >>> print(result["content"])
        
        >>> # Read last 10 lines
        >>> result = fs_read("src/main.py", mode="Line", start_line=-10, end_line=-1)
        
        >>> # List directory
        >>> result = fs_read("src/", mode="Directory", depth=2)
        >>> for entry in result["entries"]:
        ...     print(entry["path"])
        
        >>> # Search pattern
        >>> result = fs_read("src/", mode="Search", pattern="def authenticate")
        >>> for match in result["matches"]:
        ...     print(f"{match['file_path']}:{match['line_number']}")
        
        >>> # Batch operations
        >>> results = fs_read(operations=[
        ...     {"path": "file1.py", "mode": "Line"},
        ...     {"path": "src/", "mode": "Search", "pattern": "TODO"}
        ... ])
    """
    if not HAS_RUST_CORE:
        raise RuntimeError(
            "Rust core not available. Please build the Rust extension:\n"
            "  cd core && cargo build --release\n"
            "  Or install with: pip install -e ."
        )
    
    if operations:
        return _fs_read_batch(operations)
    
    result_json = contextinator_core.fs_read_py(
        path=path,
        mode=mode,
        start_line=start_line,
        end_line=end_line,
        depth=depth,
        pattern=pattern,
        context_lines=context_lines,
    )
    
    return json.loads(result_json)


def _fs_read_batch(operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Execute batch operations."""
    operations_json = [json.dumps(op) for op in operations]
    results_json = contextinator_core.fs_read_batch_py(operations_json)
    return [json.loads(r) for r in results_json]


__all__ = ["fs_read"]
