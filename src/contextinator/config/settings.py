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
    # Python
    '.py': 'python',
    '.pyi': 'python',
    '.pyw': 'python',
    
    # JavaScript/TypeScript
    '.js': 'javascript',
    '.mjs': 'javascript',
    '.cjs': 'javascript',
    '.jsx': 'jsx',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.mts': 'typescript',
    '.cts': 'typescript',
    
    # Java/JVM
    '.java': 'java',
    '.kt': 'kotlin',
    '.kts': 'kotlin',
    '.scala': 'scala',
    '.sc': 'scala',
    '.gradle': 'java',
    'build.gradle': 'java',
    'settings.gradle': 'java',
    
    # C/C++
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.hpp': 'cpp',
    '.hh': 'cpp',
    '.hxx': 'cpp',
    
    # C#
    '.cs': 'csharp',
    
    # Go
    '.go': 'go',
    
    # Rust
    '.rs': 'rust',
    
    # Zig
    '.zig': 'zig',
    
    # PHP
    '.php': 'php',
    '.phtml': 'php',
    
    # Ruby
    '.rb': 'ruby',
    '.rake': 'ruby',
    'Rakefile': 'ruby',
    'Gemfile': 'ruby',
    
    # Shell
    '.sh': 'bash',
    '.bash': 'bash',
    '.zsh': 'bash',
    '.fish': 'bash',
    
    # SQL
    '.sql': 'sql',
    
    # Swift
    '.swift': 'swift',
    
    # Solidity
    '.sol': 'solidity',
    
    # Lua
    '.lua': 'lua',
    
    # Elixir
    '.ex': 'elixir',
    '.exs': 'elixir',
    
    # Haskell
    '.hs': 'haskell',
    '.lhs': 'haskell',
    
    # OCaml
    '.ml': 'ocaml',
    '.mli': 'ocaml',
    
    # Web (HTML/CSS)
    '.html': 'html',
    '.htm': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.less': 'less',
    
    # Data formats
    '.json': 'json',
    '.jsonl': 'json',
    '.ndjson': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.xml': 'xml',
    
    # Markdown
    '.md': 'markdown',
    
    # Docker
    '.dockerfile': 'dockerfile',
    'Dockerfile': 'dockerfile',
    '.json': 'json',
    '.toml': 'toml',
    '.swift': 'swift',
    '.sol': 'solidity',
    '.lua': 'lua',
    '.ipynb': 'ipynb',
    '.prisma': 'prisma',
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
CHROMA_DB_DIR: str = '.contextinator/chromadb'  # Relative directory for ChromaDB storage
CHROMA_SERVER_URL: str = os.getenv('CHROMA_SERVER_URL', 'http://localhost:8000')
CHROMA_SERVER_AUTH_TOKEN: Optional[str] = os.getenv('CHROMA_SERVER_AUTH_TOKEN')
CHROMA_BATCH_SIZE: int = int(os.getenv('CHROMA_BATCH_SIZE', '100'))
CHUNKS_DIR: str = '.contextinator/chunks'
EMBEDDINGS_DIR: str = '.contextinator/embeddings'


def sanitize_collection_name(repo_name: str) -> str:
    """
    Sanitize repository name for use as ChromaDB collection name.
    
    Args:
        repo_name: Raw repository name
        
    Returns:
        Sanitized collection name following ChromaDB naming rules
        
    Raises:
        ValidationError: If repo_name is empty or None
    """
    from ..utils.exceptions import ValidationError
    
    if not repo_name:
        raise ValidationError("Repository name cannot be empty", "repo_name", "non-empty string")
        
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', repo_name)

    if sanitized and not sanitized[0].isalnum():
        sanitized = 'c' + sanitized
    
    if sanitized and not sanitized[-1].isalnum():
        sanitized = sanitized + '0'
    
    result = sanitized[:63] if sanitized else 'default_collection'
    return result


def get_storage_path(base_dir: Union[str, Path], storage_type: str, repo_name: str, custom_dir: Optional[str] = None) -> Path:
    """
    Get storage path for chunks/embeddings/chromadb with repository isolation.
    
    Args:
        base_dir: Base directory (e.g., repo_path or output_dir)
        storage_type: 'chunks', 'embeddings', or 'chromadb'
        repo_name: Repository name (will be sanitized)
    
    Returns:
        Path to storage directory
        
    Raises:
        ValidationError: If storage_type is not recognized or repo_name is empty
    """
    from ..utils.exceptions import ValidationError
    
    if not repo_name:
        raise ValidationError("Repository name cannot be empty", "repo_name", "non-empty string")
    
    valid_types = {'chunks', 'embeddings', 'chromadb'}
    if storage_type not in valid_types:
        raise ValidationError(
            f"Unknown storage type: {storage_type}. Must be one of: {', '.join(valid_types)}", 
            "storage_type", 
            f"one of {valid_types}"
        )
    
    safe_name = sanitize_collection_name(repo_name)
    base_path = Path(base_dir)
    
    
    # If custom directory is provided, use it as-is (already includes repo name if needed)
    if custom_dir:
        return Path(custom_dir) if Path(custom_dir).is_absolute() else base_path / custom_dir
    
    if storage_type == 'chunks':
        return base_path / CHUNKS_DIR / safe_name
    elif storage_type == 'embeddings':
        return base_path / EMBEDDINGS_DIR / safe_name
    elif storage_type == 'chromadb':
        return base_path / CHROMA_DB_DIR / safe_name


def validate_config() -> None:
    """
    Validate configuration settings and raise errors for invalid values.
    
    Raises:
        ConfigurationError: If critical configuration is invalid
    """
    from ..utils.exceptions import ConfigurationError
    
    if MAX_TOKENS <= 0:
        raise ConfigurationError("MAX_TOKENS must be positive", "MAX_TOKENS")
        
    if CHUNK_OVERLAP < 0:
        raise ConfigurationError("CHUNK_OVERLAP cannot be negative", "CHUNK_OVERLAP")
        
    if CHUNK_OVERLAP >= MAX_TOKENS:
        raise ConfigurationError("CHUNK_OVERLAP must be less than MAX_TOKENS", "CHUNK_OVERLAP")
        
    if EMBEDDING_BATCH_SIZE <= 0:
        raise ConfigurationError("EMBEDDING_BATCH_SIZE must be positive", "EMBEDDING_BATCH_SIZE")
        
    if CHROMA_BATCH_SIZE <= 0:
        raise ConfigurationError("CHROMA_BATCH_SIZE must be positive", "CHROMA_BATCH_SIZE")


def validate_openai_api_key() -> None:
    """
    Validate that OpenAI API key is set.
    
    This should be called before any operation that requires embeddings.
    
    Raises:
        ConfigurationError: If API key is not set
    """
    from ..utils.exceptions import ConfigurationError
    
    if not OPENAI_API_KEY:
        raise ConfigurationError(
            "OPENAI_API_KEY not set. Please:\n"
            "  1. Copy .env.example to .env\n"
            "  2. Add your OpenAI API key to .env\n"
            "  3. Ensure .env is in your working directory",
            "OPENAI_API_KEY"
        )


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
    'validate_openai_api_key',
]
