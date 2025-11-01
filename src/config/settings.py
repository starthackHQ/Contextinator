"""
Configuration settings for Contextinator.

This module contains all configuration constants, environment variable handling,
and validation logic for the Contextinator application.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Chunking settings
MAX_TOKENS: int = 512
CHUNK_OVERLAP: int = 50

# Supported file extensions mapping to language identifiers
SUPPORTED_EXTENSIONS: Dict[str, str] = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.java': 'java',
    '.go': 'go',
    '.cpp': 'cpp',
    '.c': 'c',
    '.rs': 'rust',
    '.cs': 'csharp',
    '.php': 'php',
    '.sh': 'bash',
    '.bash': 'bash',
    '.sql': 'sql',
    '.kt': 'kotlin',
    '.kts': 'kotlin',  # Kotlin script files
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.md': 'markdown',
    '.dockerfile': 'dockerfile',
    'Dockerfile': 'dockerfile',
    '.json': 'json',
    '.toml': 'toml',
    '.swift': 'swift',
    '.sol': 'solidity',
    '.lua': 'lua',
}

# Files/directories to ignore during processing
DEFAULT_IGNORE_PATTERNS: List[str] = [
    # Version Control
    '.git',
    '.svn',
    '.hg',
    
    # Python
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.Python',
    'pip-log.txt',
    'pip-delete-this-directory.txt',
    '.venv',
    'venv',
    'env',
    'ENV',
    '.pytest_cache',
    '.mypy_cache',
    '.tox',
    '*.egg-info',
    'dist',
    'build',
    '.eggs',
    
    # JavaScript/TypeScript/Node
    'node_modules',
    'bower_components',
    '*.min.js',
    '*.bundle.js',
    '.next',
    '.nuxt',
    'out',
    '.cache',
    '.parcel-cache',
    '.npm',
    '.yarn',
    'yarn-error.log',
    'package-lock.json',
    'yarn.lock',
    'pnpm-lock.yaml',
    
    # Java
    'target',
    '*.class',
    '*.jar',
    '*.war',
    '*.ear',
    '.gradle',
    '.mvn',
    
    # Kotlin
    '*.kt.class',
    
    # C/C++
    '*.o',
    '*.obj',
    '*.so',
    '*.dylib',
    '*.dll',
    '*.exe',
    '*.out',
    '*.a',
    '*.lib',
    'cmake-build-*',
    'CMakeFiles',
    'CMakeCache.txt',
    
    # Rust
    'target',
    'Cargo.lock',
    
    # Go
    'vendor',
    '*.test',
    
    # C#/.NET
    'bin',
    'obj',
    '*.suo',
    '*.user',
    '.vs',
    'packages',
    
    # PHP
    'vendor',
    'composer.lock',
    
    # Swift
    '.build',
    'Packages',
    '*.xcodeproj',
    '*.xcworkspace',
    'DerivedData',
    
    # Solidity
    'artifacts',
    'cache',
    
    # General
    '.DS_Store',
    'Thumbs.db',
    '*.log',
    '*.tmp',
    '*.temp',
    '*.swp',
    '*.swo',
    '*~',
    '.idea',
    '.vscode',
    '*.iml',
]

# Embedding settings
DEFAULT_EMBEDDING_MODEL: str = 'sentence-transformers/all-MiniLM-L6-v2'
OPENAI_EMBEDDING_MODEL: str = 'text-embedding-3-large'
EMBEDDING_BATCH_SIZE: int = int(os.getenv('EMBEDDING_BATCH_SIZE', '250'))
OPENAI_MAX_TOKENS: int = 8191
OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')

# Vector store settings
USE_CHROMA_SERVER: bool = os.getenv('USE_CHROMA_SERVER', 'true').lower() == 'true'
CHROMA_DB_DIR: str = '.chromadb'  # Relative directory for ChromaDB storage
CHROMA_SERVER_URL: str = os.getenv('CHROMA_SERVER_URL', 'http://localhost:8000')
CHROMA_SERVER_AUTH_TOKEN: Optional[str] = os.getenv('CHROMA_SERVER_AUTH_TOKEN')
CHROMA_BATCH_SIZE: int = int(os.getenv('CHROMA_BATCH_SIZE', '100'))
CHUNKS_DIR: str = '.chunks'
EMBEDDINGS_DIR: str = '.embeddings'


def sanitize_collection_name(repo_name: str) -> str:
    """
    Sanitize repository name for use as ChromaDB collection name.
    
    Args:
        repo_name: Raw repository name
        
    Returns:
        Sanitized collection name following ChromaDB naming rules
        
    Raises:
        ValueError: If repo_name is empty or None
    """
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', repo_name)

    if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = '_' + sanitized
    
    result = sanitized[:63] if sanitized else 'default_collection'
    return result


def get_storage_path(base_dir: Union[str, Path], storage_type: str, repo_name: str) -> Path:
    """
    Get storage path for chunks/embeddings/chromadb with repository isolation.
    
    Args:
        base_dir: Base directory (e.g., repo_path or output_dir)
        storage_type: 'chunks', 'embeddings', or 'chromadb'
        repo_name: Repository name (will be sanitized)
    
    Returns:
        Path to storage directory
        
    Raises:
        ValueError: If storage_type is not recognized
    """
    safe_name = sanitize_collection_name(repo_name)
    base_path = Path(base_dir)
    
    if storage_type == 'chunks':
        return base_path / CHUNKS_DIR / safe_name
    elif storage_type == 'embeddings':
        return base_path / EMBEDDINGS_DIR / safe_name
    elif storage_type == 'chromadb':
        return base_path / CHROMA_DB_DIR / safe_name
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")


def validate_config() -> None:
    """
    Validate configuration settings and raise errors for invalid values.
    
    Raises:
        ValueError: If critical configuration is invalid
    """
    if MAX_TOKENS <= 0:
        raise ValueError("MAX_TOKENS must be positive")
        
    if CHUNK_OVERLAP < 0:
        raise ValueError("CHUNK_OVERLAP cannot be negative")
        
    if CHUNK_OVERLAP >= MAX_TOKENS:
        raise ValueError("CHUNK_OVERLAP must be less than MAX_TOKENS")
        
    if not OPENAI_API_KEY:
        import warnings
        warnings.warn("OPENAI_API_KEY not set - OpenAI embeddings will not work")
        
    if EMBEDDING_BATCH_SIZE <= 0:
        raise ValueError("EMBEDDING_BATCH_SIZE must be positive")
        
    if CHROMA_BATCH_SIZE <= 0:
        raise ValueError("CHROMA_BATCH_SIZE must be positive")


# Export all public symbols
__all__ = [
    'MAX_TOKENS',
    'CHUNK_OVERLAP',
    'SUPPORTED_EXTENSIONS',
    'DEFAULT_IGNORE_PATTERNS',
    'DEFAULT_EMBEDDING_MODEL',
    'OPENAI_EMBEDDING_MODEL',
    'EMBEDDING_BATCH_SIZE',
    'OPENAI_MAX_TOKENS',
    'OPENAI_API_KEY',
    'USE_CHROMA_SERVER',
    'CHROMA_DB_DIR',
    'CHROMA_SERVER_URL',
    'CHROMA_SERVER_AUTH_TOKEN',
    'CHROMA_BATCH_SIZE',
    'CHUNKS_DIR',
    'EMBEDDINGS_DIR',
    'sanitize_collection_name',
    'get_storage_path',
    'validate_config',
]
