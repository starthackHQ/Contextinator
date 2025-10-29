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
    '__pycache__',
    'node_modules',
    '.git',
    '.venv',
    'venv',
    'env',
    'dist',
    'build',
    '.next',
    'target',
    '*.pyc',
    '*.min.js',
    '*.bundle.js',
]

# Embedding settings
DEFAULT_EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
EMBEDDING_BATCH_SIZE = 32

# Vector store settings
CHROMA_DB_PATH = '.chroma_db'
CHUNKS_DIR = '.chunks'
EMBEDDINGS_DIR = '.embeddings'
