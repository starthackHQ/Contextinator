"""Symbol search with async support."""
from typing import Any, Dict, List, Optional
from . import SearchTool
from ..utils.logger import logger
import asyncio

async def symbol_search(
    collection_name: str,
    symbol_name: str,
    symbol_type: Optional[str] = None,
    language: Optional[str] = None,
    exact_match: bool = True,
    chromadb_dir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search for symbols by name."""
    if not collection_name or not symbol_name:
        raise ValueError("Collection name and symbol name required")
    
    loop = asyncio.get_event_loop()
    
    def _search():
        tool = SearchTool(collection_name, chromadb_dir=chromadb_dir)
        
        where = {}
        if language:
            where["language"] = language
        if symbol_type:
            where["node_type"] = symbol_type
        if exact_match:
            where["node_name"] = symbol_name
        
        results = tool.collection.get(
            where=where if where else None,
            include=['documents', 'metadatas']
        )
        
        if not exact_match:
            filtered = {'ids': [], 'documents': [], 'metadatas': []}
            for id_, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
                if symbol_name.lower() in meta.get('node_name', '').lower():
                    filtered['ids'].append(id_)
                    filtered['documents'].append(doc)
                    filtered['metadatas'].append(meta)
            results = filtered
        
        formatted = tool.format_results(results)
        
        # Deduplicate by hash
        seen = set()
        deduped = []
        for r in formatted:
            h = r['metadata'].get('hash')
            if not h or h not in seen:
                if h:
                    seen.add(h)
                deduped.append(r)
        
        return deduped
    
    return await loop.run_in_executor(None, _search)

async def list_symbols(
    collection_name: str,
    symbol_type: Optional[str] = None,
    language: Optional[str] = None,
    file_path: Optional[str] = None
) -> List[Dict[str, str]]:
    """List all symbols in collection."""
    if not collection_name:
        raise ValueError("Collection name required")
    
    loop = asyncio.get_event_loop()
    
    def _list():
        tool = SearchTool(collection_name)
        
        where = {}
        if symbol_type:
            where["node_type"] = symbol_type
        if language:
            where["language"] = language
        
        results = tool.collection.get(
            where=where if where else None,
            include=['metadatas']
        )
        
        symbols = set()
        for meta in results['metadatas']:
            if file_path and file_path not in meta.get('file_path', ''):
                continue
            
            name = meta.get('node_name')
            node_type = meta.get('node_type')
            if name and node_type:
                symbols.add((
                    name,
                    node_type,
                    meta.get('file_path', ''),
                    meta.get('language', '')
                ))
        
        return sorted([
            {'name': n, 'type': t, 'file_path': f, 'language': l}
            for n, t, f, l in symbols
        ], key=lambda x: (x['name'], x['type']))
    
    return await loop.run_in_executor(None, _list)

__all__ = ['symbol_search', 'list_symbols']
