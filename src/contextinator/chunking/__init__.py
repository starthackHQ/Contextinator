"""Chunking module - lazy load to avoid slow tree-sitter imports."""

from .chunk_service import chunk_repository, load_chunks, save_chunks
from .file_discovery import discover_files

__all__ = [
    'chunk_repository',
    'discover_files',
    'load_chunks',
    'save_chunks',
]
