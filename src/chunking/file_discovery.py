import os
from pathlib import Path
from typing import List
from fnmatch import fnmatch
from ..config import SUPPORTED_EXTENSIONS, DEFAULT_IGNORE_PATTERNS


def discover_files(repo_path: str, ignore_patterns: List[str] = None) -> List[Path]:
    """
    Discover all supported code files in the repository.
    
    Args:
        repo_path: Path to the repository
        ignore_patterns: Additional patterns to ignore
    
    Returns:
        List of Path objects for supported files
    """
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS
    
    files = []
    repo_path = Path(repo_path)
    
    for root, dirs, filenames in os.walk(repo_path):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if not _should_ignore(d, ignore_patterns)]
        
        for filename in filenames:
            file_path = Path(root) / filename
            
            # Check if file extension is supported
            if file_path.suffix in SUPPORTED_EXTENSIONS:
                # Check if file should be ignored
                if not _should_ignore(str(file_path.relative_to(repo_path)), ignore_patterns):
                    files.append(file_path)
    
    return files


def _should_ignore(path: str, patterns: List[str]) -> bool:
    """Check if path matches any ignore pattern."""
    for pattern in patterns:
        if fnmatch(path, pattern) or pattern in path:
            return True
    return False
