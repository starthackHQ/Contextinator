"""
File discovery module for Contextinator.

This module provides functionality to discover supported source code files
in a repository while respecting ignore patterns for build artifacts,
dependencies, and other non-source files.
"""

import os
from fnmatch import fnmatch
from pathlib import Path
from typing import List, Optional, Union

from ..config import DEFAULT_IGNORE_PATTERNS, SUPPORTED_EXTENSIONS
from ..utils.logger import logger


def discover_files(
    repo_path: Union[str, Path], 
    ignore_patterns: Optional[List[str]] = None
) -> List[Path]:
    """
    Discover all supported code files in the repository.
    
    Recursively walks through the repository directory and finds files with
    supported extensions while filtering out files and directories that match
    ignore patterns (build artifacts, dependencies, etc.).
    
    Args:
        repo_path: Path to the repository to scan
        ignore_patterns: Additional patterns to ignore (extends default patterns)
    
    Returns:
        List of Path objects for supported files
        
    Raises:
        ValueError: If repo_path doesn't exist or is not a directory
    """
    repo_path = Path(repo_path)
    
    if not repo_path.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")
    if not repo_path.is_dir():
        raise ValueError(f"Repository path is not a directory: {repo_path}")
    
    # Use default ignore patterns if none provided
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS.copy()
    else:
        # Extend default patterns with custom ones
        ignore_patterns = DEFAULT_IGNORE_PATTERNS + ignore_patterns
    
    files = []
    ignored_count = 0
    
    logger.debug(f"Scanning repository: {repo_path}")
    logger.debug(f"Supported extensions: {list(SUPPORTED_EXTENSIONS.keys())}")
    
    try:
        for root, dirs, filenames in os.walk(repo_path):
            # Filter out ignored directories in-place to prevent traversal
            original_dirs = dirs.copy()
            dirs[:] = [d for d in dirs if not _should_ignore(d, ignore_patterns)]
            
            # Log ignored directories for debugging
            ignored_dirs = set(original_dirs) - set(dirs)
            if ignored_dirs:
                logger.debug(f"Ignoring directories in {root}: {ignored_dirs}")
            
            # Process files in current directory
            for filename in filenames:
                file_path = Path(root) / filename
                
                # Check if file extension is supported
                if file_path.suffix in SUPPORTED_EXTENSIONS or filename in SUPPORTED_EXTENSIONS:
                    # Check if file should be ignored
                    relative_path = str(file_path.relative_to(repo_path))
                    if not _should_ignore(relative_path, ignore_patterns):
                        files.append(file_path)
                        logger.debug(f"Found supported file: {relative_path}")
                    else:
                        ignored_count += 1
                        logger.debug(f"Ignoring file: {relative_path}")
                        
    except Exception as e:
        logger.error(f"Error during file discovery in {repo_path}: {e}")
        raise
    
    logger.info(f"File discovery complete: {len(files)} files found, {ignored_count} files ignored")
    return files


def _should_ignore(path: str, patterns: List[str]) -> bool:
    """
    Check if path matches any ignore pattern.
    
    Uses both glob-style pattern matching and substring matching
    to determine if a file or directory should be ignored.
    
    Args:
        path: File or directory path to check
        patterns: List of ignore patterns
        
    Returns:
        True if path should be ignored, False otherwise
    """
    if not path or not patterns:
        return False
        
    # Normalize path separators for cross-platform compatibility
    normalized_path = path.replace('\\', '/')
    
    for pattern in patterns:
        # Normalize pattern separators
        normalized_pattern = pattern.replace('\\', '/')
        
        # Try glob-style matching first
        if fnmatch(normalized_path, normalized_pattern):
            return True
            
        # Try substring matching for simple patterns
        if normalized_pattern in normalized_path:
            return True
            
        # Check if any path component matches the pattern
        path_parts = normalized_path.split('/')
        if any(fnmatch(part, normalized_pattern) for part in path_parts):
            return True
    
    return False


__all__ = [
    'discover_files',
]
