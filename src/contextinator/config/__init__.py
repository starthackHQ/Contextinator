"""
Configuration module for Contextinator.

This module provides centralized configuration management including
settings validation, environment variable handling, and path utilities.
"""

from .settings import (
    MAX_TOKENS,
    CHUNK_OVERLAP,
    SUPPORTED_EXTENSIONS,
    DEFAULT_IGNORE_PATTERNS,
    DEFAULT_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE,
    OPENAI_MAX_TOKENS,
    OPENAI_API_KEY,
    USE_CHROMA_SERVER,
    CHROMA_DB_DIR,
    CHROMA_SERVER_URL,
    CHROMA_SERVER_AUTH_TOKEN,
    CHROMA_BATCH_SIZE,
    CHUNKS_DIR,
    EMBEDDINGS_DIR,
    sanitize_collection_name,
    get_storage_path,
    validate_config,
    validate_openai_api_key,
)

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
