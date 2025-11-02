"""
Chunk service module for Contextinator.

This module provides the main chunking functionality that orchestrates
file discovery, AST parsing, node collection, and chunk splitting.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from concurrent.futures import ProcessPoolExecutor, as_completed

from .ast_parser import parse_file
from .ast_visualizer import save_ast_overview
from .file_discovery import discover_files
from .node_collector import NodeCollector
from .splitter import split_chunk
from ..config import CHUNKS_DIR, MAX_TOKENS, get_storage_path
from ..utils import ProgressTracker, logger


def _process_file_worker(args: tuple) -> List[Dict[str, Any]]:
    """Worker function for parallel file processing."""
    file_path, save_ast, chunks_dir, max_tokens = args
    try:
        parsed = parse_file(file_path, save_ast=save_ast, chunks_dir=chunks_dir)
        if not parsed:
            return []
        
        collector = NodeCollector()
        chunks = collector.collect_nodes(parsed)
        
        result = []
        for chunk in chunks:
            split_chunks = split_chunk(chunk, max_tokens)
            result.extend(split_chunks)
        return result
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return []


def chunk_repository(
    repo_path: Union[str, Path], 
    repo_name: Optional[str] = None, 
    save: bool = False, 
    max_tokens: int = MAX_TOKENS, 
    output_dir: Optional[Union[str, Path]] = None, 
    save_ast: bool = False,
    parallel: bool = True,
    max_workers: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Chunk a repository into semantic units with parallel processing.
    
    Args:
        repo_path: Path to the repository to chunk
        repo_name: Repository name for storage isolation (defaults to repo folder name)
        save: Whether to save chunks to disk
        max_tokens: Maximum tokens per chunk (default from config)
        output_dir: Optional output directory (defaults to current directory)
        save_ast: Whether to save AST visualization data
        parallel: Use parallel processing (default: True)
        max_workers: Number of parallel workers (default: CPU count)
    
    Returns:
        List of chunk dictionaries containing code content and metadata
        
    Raises:
        ValidationError: If repo_path doesn't exist or is not a directory
        FileSystemError: If unable to access repository or save files
    """
    from ..utils.exceptions import ValidationError, FileSystemError
    
    repo_path = Path(repo_path)
    if not repo_path.exists():
        raise ValidationError(f"Repository path does not exist: {repo_path}", "repo_path", "existing directory")
    if not repo_path.is_dir():
        raise ValidationError(f"Repository path is not a directory: {repo_path}", "repo_path", "directory")
        
    logger.info(f"Discovering files in {repo_path}...")

    try:
        files = discover_files(repo_path)
    except Exception as e:
        raise FileSystemError(f"Failed to discover files: {e}", str(repo_path), "scan")
        
    logger.info(f"Found {len(files)} files to process")
    
    if not files:
        logger.info("No supported files found")
        return []
    
    if repo_name is None:
        repo_name = repo_path.name
    actual_output_dir = Path(output_dir) if output_dir else Path.cwd()
    
    chunks_dir = get_storage_path(actual_output_dir, 'chunks', repo_name) if save_ast else None
    
    if save_ast:
        logger.info("🌳 AST visualization enabled - saving tree structures...")
    
    # Choose processing mode
    if parallel and len(files) > 1:
        all_chunks = _chunk_parallel(files, save_ast, chunks_dir, max_tokens, max_workers)
    else:
        all_chunks = _chunk_sequential(files, save_ast, chunks_dir, max_tokens)
    
    # Deduplicate across all files
    seen_hashes = set()
    unique_chunks = []
    duplicates = 0
    
    for chunk in all_chunks:
        chunk_hash = chunk.get('hash')
        if chunk_hash and chunk_hash not in seen_hashes:
            seen_hashes.add(chunk_hash)
            unique_chunks.append(chunk)
        else:
            duplicates += 1
    
    stats = {
        'total_chunks': len(all_chunks),
        'unique_hashes': len(seen_hashes),
        'duplicates_found': duplicates
    }
    
    logger.info(f"\n📊 Chunking Statistics:")
    logger.info(f"  Files processed: {len(files)}")
    logger.info(f"  Total chunks: {len(all_chunks)}")
    logger.info(f"  Unique chunks: {len(unique_chunks)}")
    logger.info(f"  Duplicates found: {duplicates}")
    
    if save:
        try:
            save_chunks(unique_chunks, actual_output_dir, repo_name, stats)
        except Exception as e:
            logger.error(f"Failed to save chunks: {e}")
    
    if save_ast and chunks_dir:
        try:
            logger.info("🌳 Creating AST overview...")
            save_ast_overview(chunks_dir)
            logger.info(f"AST files saved in: {chunks_dir / 'ast_trees'}")
        except Exception as e:
            logger.warning(f"Failed to save AST overview: {e}")
    
    return unique_chunks


def _chunk_parallel(files: List[Path], save_ast: bool, chunks_dir: Path, 
                    max_tokens: int, max_workers: Optional[int] = None) -> List[Dict[str, Any]]:
    """Parallel chunking using multiprocessing."""
    if max_workers is None:
        env_workers = os.environ.get('CONTEXTINATOR_MAX_WORKERS')
        if env_workers:
            max_workers = int(env_workers)
        else:
            max_workers = os.cpu_count() or 4
    
    logger.info(f"🚀 Using {max_workers} parallel workers")
    
    worker_args = [(f, save_ast, chunks_dir, max_tokens) for f in files]
    all_chunks = []
    progress = ProgressTracker(len(files), "Chunking files")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process_file_worker, args): args[0] for args in worker_args}
        
        for future in as_completed(futures):
            try:
                chunks = future.result()
                all_chunks.extend(chunks)
                progress.update()
            except Exception as e:
                logger.error(f"Worker failed: {e}")
                progress.update()
    
    progress.finish()
    return all_chunks


def _chunk_sequential(files: List[Path], save_ast: bool, chunks_dir: Path, 
                      max_tokens: int) -> List[Dict[str, Any]]:
    """Sequential chunking (fallback for single file or parallel=False)."""
    collector = NodeCollector()
    all_chunks = []
    failed_files = []
    progress = ProgressTracker(len(files), "Chunking files")
    
    for file_path in files:
        try:
            parsed = parse_file(file_path, save_ast=save_ast, chunks_dir=chunks_dir)
            if not parsed:
                logger.debug(f"Skipping unsupported file: {file_path}")
                progress.update()
                continue
            
            chunks = collector.collect_nodes(parsed)
            for chunk in chunks:
                try:
                    split_chunks = split_chunk(chunk, max_tokens)
                    all_chunks.extend(split_chunks)
                except Exception as e:
                    logger.warning(f"Failed to split chunk from {file_path}: {e}")
                    all_chunks.append(chunk)
                    
        except Exception as e:
            logger.warning(f"Failed to process {file_path}: {e}")
            failed_files.append(str(file_path))
        finally:
            progress.update()
    
    progress.finish()
    
    if failed_files:
        logger.warning(f"Failed to process {len(failed_files)} files")
    
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
    
    data = {
        'chunks': chunks,
        'statistics': stats or {},
        'repository': repo_name,
        'version': '1.0',
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
