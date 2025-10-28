from typing import List, Dict, Any, Set
from ..utils import hash_content


class NodeCollector:
    """Collects and deduplicates AST nodes."""
    
    def __init__(self):
        self.seen_hashes: Set[str] = set()
        self.chunks: List[Dict[str, Any]] = []
        self.duplicate_locations: Dict[str, List[str]] = {}
    
    def collect_nodes(self, parsed_file: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Collect nodes from parsed file, deduplicating by content hash.
        
        Args:
            parsed_file: Parsed file data from ast_parser
        
        Returns:
            List of unique chunks
        """
        if not parsed_file or 'nodes' not in parsed_file:
            return []
        
        collected = []
        
        for node in parsed_file['nodes']:
            content = node['content']
            content_hash = hash_content(content)
            
            # Create chunk metadata
            chunk = {
                'content': content,
                'file_path': parsed_file['file_path'],
                'language': parsed_file['language'],
                'hash': content_hash,
                'node_type': node['type'],
                'node_name': node.get('name'),
                'start_line': node['start_line'],
                'end_line': node['end_line'],
                'start_byte': node['start_byte'],
                'end_byte': node['end_byte']
            }
            
            # Track location
            location = f"{parsed_file['file_path']}:{node['start_line']}-{node['end_line']}"
            
            if content_hash in self.seen_hashes:
                # Duplicate found - track location
                if content_hash not in self.duplicate_locations:
                    self.duplicate_locations[content_hash] = []
                self.duplicate_locations[content_hash].append(location)
            else:
                # New unique chunk
                self.seen_hashes.add(content_hash)
                chunk['locations'] = [location]
                self.chunks.append(chunk)
                collected.append(chunk)
        
        return collected
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            'total_chunks': len(self.chunks),
            'unique_hashes': len(self.seen_hashes),
            'duplicates_found': len(self.duplicate_locations),
            'duplicate_locations': self.duplicate_locations
        }


def collect_nodes(parsed_file: Dict[str, Any], collector: NodeCollector = None) -> List[Dict[str, Any]]:
    """
    Convenience function to collect nodes from a parsed file.
    
    Args:
        parsed_file: Parsed file data
        collector: Optional NodeCollector instance for deduplication across files
    
    Returns:
        List of chunks
    """
    if collector is None:
        collector = NodeCollector()
    
    return collector.collect_nodes(parsed_file)
