"""
Repository utilities for Contextinator.

This module provides functions for working with Git repositories including
cloning, path resolution, and URL validation.
"""

import os
import tempfile
from subprocess import run, CalledProcessError
from typing import Optional

from .logger import logger
from .exceptions import FileSystemError


def git_root(path: Optional[str] = None) -> str:
    """
    Return the git top-level directory for path (or cwd).
    
    Args:
        path: Optional path to check. Uses cwd if None.
    
    Returns:
        Git repository root path
    
    Raises:
        FileSystemError: If not a git repository or git command fails
    """
    path_params = []
    if path:
        path_params = ['-C', str(path)]
    
    try:
        result = run(['git'] + path_params + ['rev-parse', '--show-toplevel'], 
                     capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (CalledProcessError, FileNotFoundError) as e:
        check_path = path or os.getcwd()
        raise FileSystemError(
            f"{check_path} is not a git repo. Run this in a git repository or use --path or --repo-url",
            path=check_path,
            operation="git_root"
        )


def clone_repo(repo_url: str, target_dir: Optional[str] = None) -> str:
    """
    Clone a git repository to target directory or temp directory.
    
    Args:
        repo_url: GitHub/Git repository URL
        target_dir: Optional target directory. Uses temp dir if None.
    
    Returns:
        Path to cloned repository
    
    Raises:
        FileSystemError: If cloning fails
        ValueError: If repo_url is empty
    """
    if not repo_url:
        raise ValueError("Repository URL cannot be empty")
        
    if not target_dir:
        target_dir = tempfile.mkdtemp(prefix='contextinator_')
    
    logger.info(f"📥 Cloning {repo_url}...")
    
    try:
        result = run(['git', 'clone', '--depth', '1', '--single-branch', repo_url, target_dir], 
                     capture_output=True, text=True, check=True)
        logger.info(f"Repository cloned to {target_dir}")
        return target_dir
    except (CalledProcessError, FileNotFoundError) as e:
        raise FileSystemError(
            f"Failed to clone repository: {e}",
            path=target_dir,
            operation="clone"
        )


def resolve_repo_path(repo_url: Optional[str] = None, path: Optional[str] = None) -> str:
    """
    Resolve repository path from URL, path, or current directory.
    
    Priority: repo_url > path > current directory
    
    Args:
        repo_url: Optional GitHub/Git repository URL
        path: Optional local path to repository
    
    Returns:
        Resolved repository path
        
    Raises:
        FileSystemError: If repository resolution fails
    """
    if repo_url:
        return clone_repo(repo_url)
    elif path:
        return git_root(path)
    else:
        return git_root()


def is_valid_git_url(url: Optional[str]) -> bool:
    """
    Check if URL is a valid git repository URL.
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid git URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    valid_patterns = [
        'github.com',
        'gitlab.com',
        'bitbucket.org',
        '.git'
    ]
    
    return any(pattern in url.lower() for pattern in valid_patterns)


def extract_repo_name_from_url(repo_url: Optional[str]) -> Optional[str]:
    """
    Extract repository identifier from a git URL in format: username_reponame
    
    This prevents collisions when multiple users have repos with the same name.
    
    Examples:
        https://github.com/facebook/react.git -> facebook_react
        https://github.com/vercel/next.js -> vercel_next_js
        git@github.com:user/repo.git -> user_repo
    
    Args:
        repo_url: Git repository URL
    
    Returns:
        Repository identifier as 'username_reponame' or None if URL is invalid
    """
    if not repo_url or not isinstance(repo_url, str):
        return None
    
    # Remove .git suffix if present
    url = repo_url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    
    # small monkey patch to store folders and collections using a combined identifier like `username_repo_name`
    # Extract username and repo name from path, Works for both https and git@ URLs
    parts = url.replace(':', '/').split('/')
    
    if len(parts) >= 2:
        username = parts[-2]
        repo_name = parts[-1]
        # Combine as username_reponame
        combined = f"{username}_{repo_name}"
        # Sanitize special characters (e.g., next.js -> next_js)
        combined = combined.replace('.', '_').replace('-', '_')
        return combined
    
    # Fallback: just return repo name if we can't extract username
    return parts[-1] if parts else None


__all__ = [
    'git_root',
    'clone_repo', 
    'resolve_repo_path',
    'is_valid_git_url',
    'extract_repo_name_from_url',
]
