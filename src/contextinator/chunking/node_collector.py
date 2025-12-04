"""
Node collector module for Contextinator.

This module provides functionality to collect and deduplicate AST nodes
from parsed files, tracking duplicate code across the codebase.
"""

from typing import Any, Dict, List, Optional, Set

from .context_builder import build_enriched_content
from ..utils import hash_content
from ..utils.logger import logger


class NodeCollector:
    """
    Collects and deduplicates AST nodes from parsed files.
    
    Tracks unique code chunks by content hash and maintains statistics
    about duplicates found across the codebase.
    """
    
    def __init__(self) -> None:
        """Initialize the node collector with empty state."""
        self.seen_hashes: Set[str] = set()
        self.chunks: List[Dict[str, Any]] = []
        self.duplicate_locations: Dict[str, List[str]] = {}
    
    def collect_nodes(self, parsed_file: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Collect nodes from parsed file, deduplicating by content hash.
        
        Processes all nodes from a parsed file, creates chunk metadata,
        and tracks duplicates for deduplication statistics.
        
        Args:
            parsed_file: Parsed file data from ast_parser containing 'nodes' list
        
        Returns:
            List of unique chunks from this file
            
        Raises:
            TypeError: If parsed_file is not a dictionary
            KeyError: If required keys are missing from parsed_file
        """
        if not isinstance(parsed_file, dict):
            raise TypeError("parsed_file must be a dictionary")
            
        if not parsed_file or 'nodes' not in parsed_file:
            logger.debug("No nodes found in parsed file")
            return []
        
        collected = []
        file_path = parsed_file.get('file_path', 'unknown')
        language = parsed_file.get('language', 'unknown')
        
        for node in parsed_file['nodes']:
            try:
                content = node['content']
                content_hash = hash_content(content)
                
                # Create chunk metadata first (needed for building enriched content)
                chunk_metadata = {
                    'file_path': file_path,
                    'language': language,
                    'hash': content_hash,
                    'node_type': node['type'],
                    'node_name': node.get('name'),
                    'start_line': node['start_line'],
                    'end_line': node['end_line'],
                    'start_byte': node['start_byte'],
                    'end_byte': node['end_byte']
                }
                
                # Preserve notebook-specific metadata if present
                if 'cell_index' in node:
                    chunk_metadata['cell_index'] = node['cell_index']
                if 'cell_type' in node:
                    chunk_metadata['cell_type'] = node['cell_type']
                
                # Build enriched content for better semantic search
                # This combines context metadata with code for embedding
                enriched_content = build_enriched_content(chunk_metadata, content)
                
                # Create final chunk with both original and enriched content
                chunk = {
                    'content': content,  # Original code (for display)
                    'enriched_content': enriched_content,  # Context + code (for embedding)
                    **chunk_metadata,
                    'id': node['id'],
                    'parent_id': node['parent_id'],
                    'parent_type': node['parent_type'],
                    'parent_name': node['parent_name'],
                    'children_ids': node['children_ids'],
                    'is_parent': node['is_parent']
                }
                
                # Track location for duplicate analysis
                location = f"{file_path}:{node['start_line']}-{node['end_line']}"
                
                if content_hash in self.seen_hashes:
                    # Duplicate found - track location
                    if content_hash not in self.duplicate_locations:
                        self.duplicate_locations[content_hash] = []
                    self.duplicate_locations[content_hash].append(location)
                    logger.debug(f"Duplicate code found: {location}")
                else:
                    # New unique chunk
                    self.seen_hashes.add(content_hash)
                    chunk['locations'] = [location]
                    self.chunks.append(chunk)
                    collected.append(chunk)
                    
            except (KeyError, TypeError) as e:
                logger.warning(f"Skipping malformed node in {file_path}: {e}")
                continue
        
        logger.debug(f"Collected {len(collected)} unique nodes from {file_path}")
        return collected
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Dictionary containing collection statistics including total chunks,
            unique hashes, duplicates found, and duplicate locations
        """
        return {
            'total_chunks': len(self.chunks),
            'unique_hashes': len(self.seen_hashes),
            'duplicates_found': len(self.duplicate_locations),
            'duplicate_locations': self.duplicate_locations
        }


def collect_nodes(
    parsed_file: Dict[str, Any], 
    collector: Optional[NodeCollector] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to collect nodes from a parsed file.
    
    Args:
        parsed_file: Parsed file data from ast_parser
        collector: Optional NodeCollector instance for deduplication across files
    
    Returns:
        List of chunks from the parsed file
        
    Raises:
        TypeError: If parsed_file is not a dictionary
    """
    if collector is None:
        collector = NodeCollector()
    
    return collector.collect_nodes(parsed_file)


__all__ = [
    'NodeCollector',
    'collect_nodes',
]
