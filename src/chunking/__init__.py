"""
Chunking module for Contextinator.

This module provides comprehensive functionality for parsing source code files,
extracting semantic chunks using AST analysis, and managing the chunking pipeline.

The main components include:
- File discovery with intelligent ignore patterns
- AST parsing using Tree-sitter for multiple languages  
- Semantic node extraction (functions, classes, methods)
- Chunk splitting and deduplication
- AST visualization for debugging
"""

# Core chunking functionality
from .ast_parser import parse_file
from .ast_visualizer import save_ast_overview
from .chunk_service import chunk_repository, load_chunks, save_chunks
from .context_builder import build_context
from .file_discovery import discover_files
from .node_collector import collect_nodes
from .splitter import split_chunk

__all__ = [
    'build_context',
    'chunk_repository',
    'collect_nodes',
    'discover_files',
    'load_chunks',
    'parse_file',
    'save_ast_overview',
    'save_chunks',
    'split_chunk',
]
