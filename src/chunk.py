import json
from pathlib import Path
from typing import List, Dict, Any
from .chunking import discover_files, parse_file, collect_nodes, split_chunk
from .chunking.node_collector import NodeCollector
from .utils import ProgressTracker
from .config import CHUNKS_DIR, MAX_TOKENS


def chunk_repository(repo_path: str, save: bool = False, max_tokens: int = MAX_TOKENS, output_dir: str = None) -> List[Dict[str, Any]]:
    """
    Chunk a repository into semantic units.
    
    Args:
        repo_path: Path to the repository
        save: Whether to save chunks to disk
        max_tokens: Maximum tokens per chunk
        output_dir: Optional output directory (defaults to repo_path/.chunks)
    
    Returns:
        List of chunks
    """
    print(f"Discovering files in {repo_path}...")
    files = discover_files(repo_path)
    print(f"Found {len(files)} files to process")
    
    if not files:
        print("No supported files found")
        return []
    
    # Initialize collector for deduplication
    collector = NodeCollector()
    all_chunks = []
    
    # Progress tracking
    progress = ProgressTracker(len(files), "Chunking files")
    
    for file_path in files:
        # Parse file
        parsed = parse_file(file_path)
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
    
    print(f"\n📊 Chunking Statistics:")
    print(f"  Files processed: {len(files)}")
    print(f"  Total chunks: {len(all_chunks)}")
    print(f"  Unique chunks: {stats['unique_hashes']}")
    print(f"  Duplicates found: {stats['duplicates_found']}")
    
    if save:
        save_chunks(all_chunks, output_dir or repo_path, stats)
    
    return all_chunks


def save_chunks(chunks: List[Dict[str, Any]], repo_path: str, stats: Dict[str, Any] = None):
    """Save chunks to disk."""
    chunks_dir = Path(repo_path) / CHUNKS_DIR
    chunks_dir.mkdir(exist_ok=True)
    
    output_file = chunks_dir / 'chunks.json'
    
    # Prepare data to save
    data = {
        'chunks': chunks,
        'statistics': stats or {}
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Chunks saved to {output_file}")


def load_chunks(repo_path: str) -> List[Dict[str, Any]]:
    """Load chunks from disk."""
    chunks_file = Path(repo_path) / CHUNKS_DIR / 'chunks.json'
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both old and new format
    if isinstance(data, list):
        return data
    return data.get('chunks', [])
