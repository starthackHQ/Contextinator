"""
Chunk service module for Contextinator.

This module provides the main chunking functionality that orchestrates
file discovery, AST parsing, node collection, and chunk splitting.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .ast_parser import parse_file
from .ast_visualizer import save_ast_overview
from .file_discovery import discover_files
from .node_collector import NodeCollector
from .splitter import split_chunk
from ..config import CHUNKS_DIR, MAX_TOKENS, get_storage_path
from ..utils import ProgressTracker, logger


def chunk_repository(
    repo_path: Union[str, Path], 
    repo_name: Optional[str] = None, 
    save: bool = False, 
    max_tokens: int = MAX_TOKENS, 
    output_dir: Optional[Union[str, Path]] = None, 
    save_ast: bool = False
) -> List[Dict[str, Any]]:
    """
    Chunk a repository into semantic units using AST parsing.
    
    This function discovers supported files in a repository, parses them using
    Tree-sitter to extract semantic nodes (functions, classes, etc.), and
    creates chunks suitable for embedding and vector storage.
    
    Args:
        repo_path: Path to the repository to chunk
        repo_name: Repository name for storage isolation (defaults to repo folder name)
        save: Whether to save chunks to disk
        max_tokens: Maximum tokens per chunk (default from config)
        output_dir: Optional output directory (defaults to current directory)
        save_ast: Whether to save AST visualization data for debugging
    
    Returns:
        List of chunk dictionaries containing code content and metadata
        
    Raises:
        ValueError: If repo_path doesn't exist or is not a directory
    """
    repo_path = Path(repo_path)
    if not repo_path.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")
    if not repo_path.is_dir():
        raise ValueError(f"Repository path is not a directory: {repo_path}")
        
    logger.info(f"Discovering files in {repo_path}...")
    files = discover_files(repo_path)
    logger.info(f"Found {len(files)} files to process")
    
    if not files:
        logger.info("No supported files found")
        return []
    
    # Determine repository name and output directory
    if repo_name is None:
        repo_name = repo_path.name
    actual_output_dir = Path(output_dir) if output_dir else Path.cwd()
    
    # Get repository-specific chunks directory for AST storage
    chunks_dir = get_storage_path(actual_output_dir, 'chunks', repo_name) if save_ast else None
    
    # Initialize collector for deduplication
    collector = NodeCollector()
    all_chunks = []
    
    # Progress tracking
    progress = ProgressTracker(len(files), "Chunking files")
    
    if save_ast:
        logger.info("🌳 AST visualization enabled - saving tree structures...")
        logger.info("   Using installed tree-sitter language modules...")
    
    # Process each file
    for file_path in files:
        try:
            # Parse file with optional AST saving
            parsed = parse_file(file_path, save_ast=save_ast, chunks_dir=chunks_dir)
            if not parsed:
                progress.update()
                continue
            
            # Collect nodes (with deduplication)
            chunks = collector.collect_nodes(parsed)
            
            # Split large chunks if needed
            for chunk in chunks:
                split_chunks = split_chunk(chunk, max_tokens)
                all_chunks.extend(split_chunks)
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
        finally:
            progress.update()
    
    progress.finish()
    
    # Get statistics
    stats = collector.get_stats()
    
    logger.info("\n📊 Chunking Statistics:")
    logger.info(f"  Files processed: {len(files)}")
    logger.info(f"  Total chunks: {len(all_chunks)}")
    logger.info(f"  Unique chunks: {stats['unique_hashes']}")
    logger.info(f"  Duplicates found: {stats['duplicates_found']}")
    
    # Save chunks if requested
    if save:
        save_chunks(all_chunks, actual_output_dir, repo_name, stats)
    
    # Save AST overview if requested
    if save_ast and chunks_dir:
        logger.info("🌳 Creating AST overview...")
        save_ast_overview(chunks_dir)
        logger.info(f"AST files saved in: {chunks_dir / 'ast_trees'}")
    
    return all_chunks


def save_chunks(
    chunks: List[Dict[str, Any]], 
    base_dir: Union[str, Path], 
    repo_name: str, 
    stats: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Save chunks to repository-specific directory.
    
    Args:
        chunks: List of chunks to save
        base_dir: Base output directory
        repo_name: Repository name for isolation
        stats: Optional statistics to include in output
        
    Returns:
        Path to the saved chunks file
        
    Raises:
        ValueError: If repo_name is empty
        OSError: If unable to create directory or write file
    """
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    chunks_dir = get_storage_path(base_dir, 'chunks', repo_name)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = chunks_dir / 'chunks.json'
    
    # Prepare data to save
    data = {
        'chunks': chunks,
        'statistics': stats or {},
        'repository': repo_name,
        'version': '1.0',  # For future compatibility
        'total_chunks': len(chunks)
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ Chunks saved to {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Failed to save chunks to {output_file}: {e}")
        raise


def load_chunks(base_dir: Union[str, Path], repo_name: str) -> List[Dict[str, Any]]:
    """
    Load chunks from repository-specific directory.
    
    Args:
        base_dir: Base directory containing .chunks folder
        repo_name: Repository name for isolation
    
    Returns:
        List of chunks
        
    Raises:
        ValueError: If repo_name is empty
        FileNotFoundError: If chunks file doesn't exist
        json.JSONDecodeError: If chunks file is corrupted
    """
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    chunks_file = get_storage_path(base_dir, 'chunks', repo_name) / 'chunks.json'
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
    
    logger.info(f"📂 Loading chunks from {chunks_file}")
    
    try:
        with open(chunks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both old and new format for backward compatibility
        if isinstance(data, list):
            logger.debug("Loading chunks in legacy format")
            return data
            
        chunks = data.get('chunks', [])
        logger.info(f"Loaded {len(chunks)} chunks from {repo_name}")
        return chunks
        
    except json.JSONDecodeError as e:
        logger.error(f"Corrupted chunks file {chunks_file}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading chunks from {chunks_file}: {e}")
        raise


__all__ = [
    'chunk_repository',
    'save_chunks', 
    'load_chunks',
]
