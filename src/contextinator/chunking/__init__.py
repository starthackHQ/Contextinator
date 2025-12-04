"""Chunking module - lazy load to avoid slow tree-sitter imports."""

from .chunk_service import chunk_repository, load_chunks, save_chunks
from .file_discovery import discover_files
from .notebook_parser import parse_notebook

__all__ = [
    'chunk_repository',
    'discover_files',
    'load_chunks',
    'save_chunks',
    'parse_notebook',
]
