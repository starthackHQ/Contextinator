import json
from pathlib import Path
from typing import List, Dict, Any
from . import discover_files, parse_file, split_chunk, save_ast_overview
from .node_collector import NodeCollector
from ..utils import ProgressTracker, logger
from ..config import CHUNKS_DIR, MAX_TOKENS


def chunk_repository(repo_path: str, repo_name: str = None, save: bool = False, max_tokens: int = MAX_TOKENS, 
                     output_dir: str = None, save_ast: bool = False) -> List[Dict[str, Any]]:
    """
    Chunk a repository into semantic units.
    
    Args:
        repo_path: Path to the repository
        repo_name: Repository name for storage isolation (defaults to repo folder name)
        save: Whether to save chunks to disk
        max_tokens: Maximum tokens per chunk
        output_dir: Optional output directory (defaults to current directory)
        save_ast: Whether to save AST visualization data
    
    Returns:
        List of chunks
    """
    logger.info(f"Discovering files in {repo_path}...")
    files = discover_files(repo_path)
    logger.info(f"Found {len(files)} files to process")
    
    if not files:
        logger.info(f"No supported files found")
        return []
    
    # Determine repository name and output directory
    if repo_name is None:
        repo_name = Path(repo_path).name
    actual_output_dir = output_dir or Path.cwd()
    
    # Get repository-specific chunks directory for AST storage
    from ..config import get_storage_path
    chunks_dir = get_storage_path(actual_output_dir, 'chunks', repo_name) if save_ast else None
    
    # Initialize collector for deduplication
    collector = NodeCollector()
    all_chunks = []
    
    # Progress tracking
    progress = ProgressTracker(len(files), "Chunking files")
    
    if save_ast:
        logger.info("🌳 AST visualization enabled - saving tree structures...")
        logger.info("   Using installed tree-sitter language modules...")
    
    for file_path in files:
        # Parse file with optional AST saving
        parsed = parse_file(file_path, save_ast=save_ast, chunks_dir=chunks_dir)
        if not parsed:
            progress.update()
            continue
        
        # Collect nodes (with deduplication)
        chunks = collector.collect_nodes(parsed)
        
        # Split large chunks
        for chunk in chunks:
            split_chunks = split_chunk(chunk, max_tokens)
            all_chunks.extend(split_chunks)
        
        progress.update()
    
    progress.finish()
    
    # Get statistics
    stats = collector.get_stats()
    
    logger.info("\n📊 Chunking Statistics:")
    logger.info(f"  Files processed: {len(files)}")
    logger.info(f"  Total chunks: {len(all_chunks)}")
    logger.info(f"  Unique chunks: {stats['unique_hashes']}")
    logger.info(f"  Duplicates found: {stats['duplicates_found']}")
    
    if save:
        save_chunks(all_chunks, actual_output_dir, repo_name, stats)
    
    if save_ast:
        logger.info("🌳 Creating AST overview...")
        save_ast_overview(chunks_dir)
        logger.info(f"AST files saved in: {chunks_dir / 'ast_trees'}")
    
    return all_chunks


def save_chunks(chunks: List[Dict[str, Any]], base_dir: str, repo_name: str, stats: Dict[str, Any] = None):
    """
    Save chunks to repository-specific directory.
    
    Args:
        chunks: List of chunks to save
        base_dir: Base output directory
        repo_name: Repository name for isolation
        stats: Optional statistics
    """
    from ..config import get_storage_path
    
    chunks_dir = get_storage_path(base_dir, 'chunks', repo_name)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = chunks_dir / 'chunks.json'
    
    # Prepare data to save
    data = {
        'chunks': chunks,
        'statistics': stats or {},
        'repository': repo_name
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n✅ Chunks saved to {output_file}")


def load_chunks(base_dir: str, repo_name: str) -> List[Dict[str, Any]]:
    """
    Load chunks from repository-specific directory.
    
    Args:
        base_dir: Base directory containing .chunks folder
        repo_name: Repository name for isolation
    
    Returns:
        List of chunks
    """
    from ..config import get_storage_path
    
    chunks_file = get_storage_path(base_dir, 'chunks', repo_name) / 'chunks.json'
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
    
    logger.info(f"📂 Loading chunks from {chunks_file}")
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both old and new format
    if isinstance(data, list):
        return data
    return data.get('chunks', [])
