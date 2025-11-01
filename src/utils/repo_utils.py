import os
import sys
import tempfile
from subprocess import run
from pathlib import Path
from ..utils.logger import logger


def git_root(path=None):
    """
    Return the git top-level directory for path (or cwd).
    
    Args:
        path: Optional path to check. Uses cwd if None.
    
    Returns:
        str: Git repository root path
    
    Raises:
        SystemExit: If not a git repository
    """
    path_params = []
    if path:
        path_params = ['-C', path]
    
    result = run(['git'] + path_params + ['rev-parse', '--show-toplevel'], 
                 capture_output=True, text=True)
    
    if result.returncode != 0:
        if not path:
            path = os.getcwd()
        logger.error("{path} is not a git repo. Run this in a git repository or use --path or --repo-url")
        sys.exit(1)
    
    return result.stdout.strip()


def clone_repo(repo_url, target_dir=None):
    """
    Clone a git repository to target directory or temp directory.
    
    Args:
        repo_url: GitHub/Git repository URL
        target_dir: Optional target directory. Uses temp dir if None.
    
    Returns:
        str: Path to cloned repository
    
    Raises:
        SystemExit: If cloning fails
    """
    if not target_dir:
        target_dir = tempfile.mkdtemp(prefix='contextinator_')
    
    logger.info("📥 Cloning {repo_url}...")
    result = run(['git', 'clone', '--depth', '1', repo_url, target_dir], 
                 capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error("Failed to clone repository: {result.stderr}")
        sys.exit(1)
    
    logger.info("Repository cloned to {target_dir}")
    return target_dir


def resolve_repo_path(repo_url=None, path=None):
    """
    Resolve repository path from URL, path, or current directory.
    
    Priority: repo_url > path > current directory
    
    Args:
        repo_url: Optional GitHub/Git repository URL
        path: Optional local path to repository
    
    Returns:
        str: Resolved repository path
    """
    if repo_url:
        return clone_repo(repo_url)
    elif path:
        return git_root(path)
    else:
        return git_root()


def is_valid_git_url(url):
    """
    Check if URL is a valid git repository URL.
    
    Args:
        url: URL to validate
    
    Returns:
        bool: True if valid git URL
    """
    if not url:
        return False
    
    valid_patterns = [
        'github.com',
        'gitlab.com',
        'bitbucket.org',
        '.git'
    ]
    
    return any(pattern in url.lower() for pattern in valid_patterns)


def extract_repo_name_from_url(repo_url):
    """
    Extract repository name from a git URL.
    
    Examples:
        https://github.com/user/repo.git -> repo
        https://github.com/user/repo -> repo
        git@github.com:user/repo.git -> repo
    
    Args:
        repo_url: Git repository URL
    
    Returns:
        str: Repository name
    """
    if not repo_url:
        return None
    
    # Remove .git suffix if present
    url = repo_url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    
    # Extract last part of path (repository name)
    # Works for both https and git@ URLs
    parts = url.replace(':', '/').split('/')
    return parts[-1] if parts else None
