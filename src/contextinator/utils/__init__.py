"""
Utility modules for Contextinator.

This module provides common utilities including logging, progress tracking,
repository operations, token counting, hashing functionality, and custom exceptions.
"""

from .exceptions import (
    ConfigurationError,
    ContextinatorError,
    EmbeddingError,
    FileSystemError,
    ParsingError,
    SearchError,
    ValidationError,
    VectorStoreError,
)
from .hash_utils import hash_content
from .logger import logger, setup_logger
from .progress import ProgressTracker
from .repo_utils import (
    clone_repo,
    git_root,
    is_valid_git_url,
    resolve_repo_path,
)
from .token_counter import count_tokens
from .toon_encoder import toon_encode

__all__ = [
    'ConfigurationError',
    'ContextinatorError',
    'EmbeddingError',
    'FileSystemError',
    'ParsingError',
    'SearchError',
    'ValidationError',
    'VectorStoreError',
    'clone_repo',
    'count_tokens',
    'git_root',
    'hash_content',
    'is_valid_git_url',
    'logger',
    'ProgressTracker',
    'resolve_repo_path',
    'setup_logger',
    'toon_encode',
]
