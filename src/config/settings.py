import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration settings for SemanticSage

# Chunking settings
MAX_TOKENS = 512
CHUNK_OVERLAP = 50

# Supported file extensions
SUPPORTED_EXTENSIONS = {
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

# Files/directories to ignore
DEFAULT_IGNORE_PATTERNS = [
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
DEFAULT_EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
OPENAI_EMBEDDING_MODEL = 'text-embedding-3-large'
EMBEDDING_BATCH_SIZE = int(os.getenv('EMBEDDING_BATCH_SIZE', '250'))
OPENAI_MAX_TOKENS = 8191
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Vector store settings
USE_CHROMA_SERVER = os.getenv('USE_CHROMA_SERVER', 'true').lower() == 'true'
CHROMA_DB_DIR = '.chromadb'  # Relative directory for ChromaDB storage
CHROMA_SERVER_URL = os.getenv('CHROMA_SERVER_URL', 'http://localhost:8000')
CHROMA_SERVER_AUTH_TOKEN = os.getenv('CHROMA_SERVER_AUTH_TOKEN')
CHROMA_BATCH_SIZE = int(os.getenv('CHROMA_BATCH_SIZE', '100'))
CHUNKS_DIR = '.chunks'
EMBEDDINGS_DIR = '.embeddings'

# Collection naming
def sanitize_collection_name(repo_name: str) -> str:
    """Sanitize repository name for use as ChromaDB collection name."""
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', repo_name)

    if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = '_' + sanitized
    return sanitized[:63] if sanitized else 'default_collection'


def get_storage_path(base_dir: str, storage_type: str, repo_name: str):
    """
    Get storage path for chunks/embeddings/chromadb with repository isolation.
    
    Args:
        base_dir: Base directory (e.g., repo_path or output_dir)
        storage_type: 'chunks', 'embeddings', or 'chromadb'
        repo_name: Repository name (will be sanitized)
    
    Returns:
        Path to storage directory
    """
    from pathlib import Path
    
    safe_name = sanitize_collection_name(repo_name)
    
    if storage_type == 'chunks':
        return Path(base_dir) / CHUNKS_DIR / safe_name
    elif storage_type == 'embeddings':
        return Path(base_dir) / EMBEDDINGS_DIR / safe_name
    elif storage_type == 'chromadb':
        return Path(base_dir) / CHROMA_DB_DIR / safe_name
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
