"""
Chunk service module for Contextinator.

This module provides the main chunking functionality that orchestrates
file discovery, AST parsing, node collection, and chunk splitting.
"""

import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Lazy import ast_parser to avoid slow tree-sitter loading
from .file_discovery import discover_files
from ..config import CHUNKS_DIR, MAX_TOKENS, get_storage_path
from ..utils import ProgressTracker, logger


def _process_file(file_path: Path, repo_path: Path, max_tokens: int) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Process single file (for parallel execution)."""
    from .ast_parser import parse_file
    from .node_collector import NodeCollector
    from .splitter import split_chunk
    
    try:
        parsed = parse_file(file_path, save_ast=False, repo_path=repo_path)
        if not parsed:
            return [], None
        
        collector = NodeCollector()
        chunks = collector.collect_nodes(parsed)
        
        all_chunks = []
        for chunk in chunks:
            try:
                split_chunks = split_chunk(chunk, max_tokens)
                all_chunks.extend(split_chunks)
            except Exception:
                all_chunks.append(chunk)
        
        return all_chunks, None
    except Exception as e:
        return [], str(file_path)


def chunk_repository(
    repo_path: Union[str, Path], 
    repo_name: Optional[str] = None, 
    save: bool = False, 
    max_tokens: int = MAX_TOKENS, 
    output_dir: Optional[Union[str, Path]] = None, 
    save_ast: bool = False,
    custom_chunks_dir: Optional[str] = None,
    use_parallel: bool = True
) -> List[Dict[str, Any]]:
    """
    Chunk a repository into semantic units using AST parsing.
    
    Args:
        repo_path: Path to the repository to chunk
        repo_name: Repository name for storage isolation
        save: Whether to save chunks to disk
        max_tokens: Maximum tokens per chunk
        output_dir: Optional output directory
        save_ast: Whether to save AST visualization data
        use_parallel: Use parallel processing (default: True)
    
    Returns:
        List of chunk dictionaries
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
    
    chunks_dir = get_storage_path(actual_output_dir, 'chunks', repo_name, custom_chunks_dir) if save_ast else None
    
    all_chunks = []
    failed_files = []
    
    # Use parallel processing for 10+ files
    if use_parallel and len(files) > 10:
        logger.info(f"⚡ Using parallel processing ({cpu_count()-1} workers)...")
        progress = ProgressTracker(len(files), "Chunking files")
        
        max_workers = max(1, cpu_count() - 1)
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_process_file, f, repo_path, max_tokens): f for f in files}
            
            for future in as_completed(futures):
                chunks, error = future.result()
                all_chunks.extend(chunks)
                if error:
                    failed_files.append(error)
                progress.update()
        
        progress.finish()
    else:
        # Sequential processing - lazy import here
        from .ast_parser import parse_file
        from .node_collector import NodeCollector
        from .splitter import split_chunk
        from .ast_visualizer import save_ast_overview
        
        collector = NodeCollector()
        progress = ProgressTracker(len(files), "Chunking files")
        
        for file_path in files:
            try:
                parsed = parse_file(file_path, save_ast=save_ast, chunks_dir=chunks_dir, repo_path=repo_path)
                if not parsed:
                    progress.update()
                    continue
                
                chunks = collector.collect_nodes(parsed)
                
                for chunk in chunks:
                    try:
                        split_chunks = split_chunk(chunk, max_tokens)
                        all_chunks.extend(split_chunks)
                    except Exception:
                        all_chunks.append(chunk)
                        
            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")
                failed_files.append(str(file_path))
            finally:
                progress.update()
        
        progress.finish()
    
    if failed_files:
        logger.warning(f"Failed to process {len(failed_files)} files")
    
    logger.info(f"\n📊 Chunking Statistics:")
    logger.info(f"  Files processed: {len(files) - len(failed_files)}/{len(files)}")
    logger.info(f"  Total chunks: {len(all_chunks)}")
    
    if save:
        try:
            save_chunks(all_chunks, actual_output_dir, repo_name, {}, custom_chunks_dir)
        except Exception as e:
            logger.error(f"Failed to save chunks: {e}")
    
    if save_ast and chunks_dir:
        try:
            from .ast_visualizer import save_ast_overview
            save_ast_overview(chunks_dir)
        except Exception as e:
            logger.warning(f"Failed to save AST overview: {e}")
    
    return all_chunks


def save_chunks(
    chunks: List[Dict[str, Any]], 
    base_dir: Union[str, Path], 
    repo_name: str, 
    stats: Optional[Dict[str, Any]] = None,
    custom_chunks_dir: Optional[str] = None
) -> Path:
    """Save chunks to repository-specific directory."""
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    chunks_dir = get_storage_path(base_dir, 'chunks', repo_name, custom_chunks_dir)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = chunks_dir / 'chunks.json'
    
    data = {
        'chunks': chunks,
        'statistics': stats or {},
        'repository': repo_name,
        'version': '2.0',
        'total_chunks': len(chunks),
        'schema': {
            'parent_child_enabled': True,
            'hierarchy_fields': ['id', 'parent_id', 'parent_type', 'parent_name', 'children_ids', 'is_parent']
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n✅ Chunks saved to {output_file}")
    return output_file


def load_chunks(base_dir: Union[str, Path], repo_name: str) -> List[Dict[str, Any]]:
    """Load chunks from repository-specific directory."""
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    chunks_file = get_storage_path(base_dir, 'chunks', repo_name) / 'chunks.json'
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
    
    logger.info(f"📂 Loading chunks from {chunks_file}")
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return data
            
    chunks = data.get('chunks', [])
    logger.info(f"Loaded {len(chunks)} chunks from {repo_name}")
    return chunks


__all__ = [
    'chunk_repository',
    'save_chunks', 
    'load_chunks',
]
