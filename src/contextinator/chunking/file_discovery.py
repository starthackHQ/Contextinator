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
        ValidationError: If repo_path doesn't exist or is not a directory
        FileSystemError: If unable to access repository directory
    """
    from ..utils.exceptions import ValidationError, FileSystemError
    
    repo_path = Path(repo_path)
    
    if not repo_path.exists():
        raise ValidationError(f"Repository path does not exist: {repo_path}", "repo_path", "existing path")
    if not repo_path.is_dir():
        raise ValidationError(f"Repository path is not a directory: {repo_path}", "repo_path", "directory")
    
    # Use default ignore patterns if none provided
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS.copy()
    else:
        # Extend default patterns with custom ones
        ignore_patterns = DEFAULT_IGNORE_PATTERNS + ignore_patterns
    
    files = []
    ignored_count = 0
    permission_errors = []
    
    logger.debug(f"Scanning repository: {repo_path}")
    logger.debug(f"Supported extensions: {list(SUPPORTED_EXTENSIONS.keys())}")
    
    try:
        # Handle permission errors gracefully, continue scanning
        for root, dirs, filenames in os.walk(repo_path):
            try:
                # Filter out ignored directories in-place to prevent traversal
                original_dirs = dirs.copy()
                dirs[:] = [d for d in dirs if not _should_ignore(d, ignore_patterns)]
                
                # Log ignored directories for debugging
                ignored_dirs = set(original_dirs) - set(dirs)
                if ignored_dirs:
                    logger.debug(f"Ignoring directories in {root}: {ignored_dirs}")
                
                # Process files in current directory
                for filename in filenames:
                    try:
                        file_path = Path(root) / filename
                        
                        # Check if file extension is supported
                        if file_path.suffix in SUPPORTED_EXTENSIONS or filename in SUPPORTED_EXTENSIONS:
                            # Check if file should be ignored
                            relative_path = str(file_path.relative_to(repo_path))
                            if not _should_ignore(relative_path, ignore_patterns):
                                # File is valid - os.walk already confirms existence
                                # No need for additional stat() call
                                files.append(file_path)
                                logger.debug(f"Found supported file: {relative_path}")
                            else:
                                ignored_count += 1
                                logger.debug(f"Ignoring file: {relative_path}")
                                
                    except Exception as e:
                        # Log individual file errors and continue
                        logger.debug(f"Error processing file {filename}: {e}")
                        continue
                        
            except (PermissionError, OSError) as e:
                # Log directory access errors and continue
                logger.warning(f"Cannot access directory {root}: {e}")
                continue
                        
    except Exception as e:
        raise FileSystemError(f"Error during file discovery: {e}", str(repo_path), "scan")
    
    # Report results
    if permission_errors:
        logger.warning(f"Skipped {len(permission_errors)} files due to permission errors")
        logger.debug(f"Permission errors: {permission_errors[:5]}{'...' if len(permission_errors) > 5 else ''}")
    
    logger.info(f"File discovery complete: {len(files)} files found, {ignored_count} files ignored")
    return files


def _should_ignore(path: str, patterns: List[str]) -> bool:
    """
    Check if path matches any ignore pattern.
    
    Uses glob-style pattern matching and exact path component matching
    to determine if a file or directory should be ignored.
    
    Args:
        path: File or directory path to check
        patterns: List of ignore patterns
        
    Returns:
        True if path should be ignored, False otherwise
    """
    if not path or not patterns:
        return False
        
    # Normalize path separators for cross-platform compatibility (done once)
    normalized_path = path.replace('\\', '/')
    # Split path once for component matching
    path_parts = normalized_path.split('/')
    
    for pattern in patterns:
        # Normalize pattern separators
        normalized_pattern = pattern.replace('\\', '/')
        
        # Check if pattern has wildcards before doing expensive fnmatch
        has_wildcards = '*' in normalized_pattern or '?' in normalized_pattern or '[' in normalized_pattern
        
        if has_wildcards:
            # Try glob-style matching on full path
            if fnmatch(normalized_path, normalized_pattern):
                return True
            
            # Check if any path component matches the pattern
            if any(fnmatch(part, normalized_pattern) for part in path_parts):
                return True
        else:
            # For non-wildcard patterns, only match exact path components
            # This prevents "out" from matching "routes"
            if any(part == normalized_pattern for part in path_parts):
                return True
    
    return False


__all__ = [
    'discover_files',
]
