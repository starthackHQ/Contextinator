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
EMBEDDING_BATCH_SIZE = 32

# Vector store settings
CHROMA_DB_PATH = '.chroma_db'
CHUNKS_DIR = '.chunks'
EMBEDDINGS_DIR = '.embeddings'
