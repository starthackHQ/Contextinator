"""
ChromaDB vector store module for Contextinator.

This module provides functionality for storing and managing code embeddings
in ChromaDB, with support for both local persistence and server connections.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import chromadb
from chromadb.config import Settings

from ..config import (
    CHROMA_BATCH_SIZE,
    CHROMA_DB_DIR,
    CHROMA_SERVER_URL,
    USE_CHROMA_SERVER,
    get_storage_path,
    sanitize_collection_name,
)
from ..utils import ProgressTracker, logger


class ChromaVectorStore:
    """
    ChromaDB vector store for semantic code search.
    
    Provides functionality to store, retrieve, and manage code embeddings
    with support for both local persistence and remote server connections.
    """
    
    def __init__(
        self, 
        db_path: Optional[str] = None, 
        base_dir: Optional[Union[str, Path]] = None, 
        repo_name: Optional[str] = None,
        custom_chromadb_dir: Optional[str] = None
    ) -> None:
        """
        Initialize ChromaDB vector store.
        
        Args:
            db_path: Explicit path to ChromaDB database (overrides base_dir/repo_name)
            base_dir: Base directory for relative path construction
            repo_name: Repository name for path construction
            
        Raises:
            RuntimeError: If ChromaDB client initialization fails
        """
        if db_path:
            self.db_path = db_path
        elif base_dir and repo_name:
            self.db_path = str(get_storage_path(base_dir, 'chromadb', repo_name, custom_chromadb_dir))
        else:
            # Fallback to current directory if nothing provided
            self.db_path = str(Path.cwd() / CHROMA_DB_DIR / 'default')
        
        self.client: Optional[chromadb.Client] = None
        self.using_server = False  # Track if we're using server mode
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """
        Initialize ChromaDB client with fallback from server to local.
        
        Raises:
            VectorStoreError: If both server and local client initialization fail
        """
        from ..utils.exceptions import VectorStoreError
        
        # Try server first, fallback to local
        if USE_CHROMA_SERVER:
            try:
                logger.info(f"Connecting to ChromaDB server at: {CHROMA_SERVER_URL}")
                # Parse URL to get host and port
                from urllib.parse import urlparse
                parsed_url = urlparse(CHROMA_SERVER_URL)
                host = parsed_url.hostname or "localhost"
                port = parsed_url.port or 8000
                self.client = chromadb.HttpClient(host=host, port=port)
                
                # Test connection
                self.client.heartbeat()
                logger.info("ChromaDB server connection successful")
                self.using_server = True  # Mark that we're using server
                return
                
            except Exception as e:
                logger.warning(f"ChromaDB server connection failed: {e}")
                logger.info("🔄 Falling back to local persistence...")
                # Continue to local fallback
        
        # Initialize local client (either by choice or as fallback)
        try:
            self._initialize_local_client()
            self.using_server = False  # Mark that we're using local
        except Exception as e:
            if USE_CHROMA_SERVER:
                raise VectorStoreError(f"Both server and local ChromaDB initialization failed: {e}", "initialize")
            else:
                raise VectorStoreError(f"Local ChromaDB initialization failed: {e}", "initialize")
    
    def _initialize_local_client(self) -> None:
        """
        Initialize local ChromaDB client with persistence.
        
        Raises:
            VectorStoreError: If local client initialization fails
        """
        from ..utils.exceptions import VectorStoreError, FileSystemError
        
        try:
            os.makedirs(self.db_path, exist_ok=True)
        except Exception as e:
            raise FileSystemError(f"Cannot create ChromaDB directory: {e}", self.db_path, "create")
            
        try:
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"ChromaDB local persistence at: {self.db_path}")
        except Exception as e:
            raise VectorStoreError(f"Failed to create local ChromaDB client: {e}", "initialize")
    
    def _get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        """
        Get or create a collection for the repository.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaDB collection instance
            
        Raises:
            VectorStoreError: If collection creation/retrieval fails
        """
        from ..utils.exceptions import VectorStoreError
        
        if not self.client:
            raise VectorStoreError("ChromaDB client not initialized", "get_collection")
            
        try:
            safe_name = sanitize_collection_name(collection_name)
            
            # Try to get existing collection, fallback to create new
            try:
                collection = self.client.get_collection(name=safe_name)
                logger.info(f"Using existing collection: {safe_name}")
                return collection
            except Exception:
                # Collection doesn't exist, create it
                collection = self.client.create_collection(
                    name=safe_name,
                    metadata={"description": f"Code chunks for repository: {collection_name}"}, embedding_function=None
                )
                logger.info(f"Created new collection: {safe_name}")
                return collection
                
        except Exception as e:
            raise VectorStoreError(f"Failed to get/create collection '{collection_name}': {e}", "get_collection", collection_name)
    
    def _prepare_batch_data(self, embedded_chunks: List[Dict[str, Any]]) -> Tuple[List[str], List[List[float]], List[Dict[str, Any]], List[str]]:
        """
        Prepare batch data for ChromaDB insertion.
        
        Args:
            embedded_chunks: List of chunks with embeddings
            
        Returns:
            Tuple of (ids, embeddings, metadatas, documents)
            
        Raises:
            ValueError: If chunk is missing embedding
        """
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for i, chunk in enumerate(embedded_chunks):
            # Use existing chunk ID if available, otherwise generate one
            # This avoids redundant hash computation
            chunk_id = chunk.get('id')
            if not chunk_id:
                # Fallback: generate ID from index and content hash
                chunk_id = f"chunk_{i}_{chunk.get('hash', hash(chunk.get('content', '')))}"
            ids.append(chunk_id)
            
            # Extract embedding
            embedding = chunk.get('embedding')
            if not embedding:
                raise ValueError(f"Chunk at index {i} missing embedding")
            embeddings.append(embedding)
            
            # Prepare metadata (exclude embedding and enriched_content to avoid duplication)
            # enriched_content is excluded because it's stored in documents field
            metadata = {k: v for k, v in chunk.items() if k not in ['embedding', 'enriched_content']}
            metadata = self._sanitize_metadata(metadata)
            metadatas.append(metadata)
            
            # Store original content in documents field (for display in search results)
            # The enriched_content was used for embedding, but we display original content
            documents.append(chunk.get('content', ''))
        
        return ids, embeddings, metadatas, documents
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize metadata to ensure ChromaDB compatibility.
        
        ChromaDB has restrictions on metadata types and keys.
        
        Args:
            metadata: Raw metadata dictionary
            
        Returns:
            Sanitized metadata dictionary
        """
        sanitized = {}
        
        for key, value in metadata.items():
            # Sanitize key (replace problematic characters)
            str_key = str(key).replace('.', '_').replace(' ', '_')
            
            # Convert value to ChromaDB-compatible type
            if isinstance(value, (str, int, float, bool)):
                sanitized[str_key] = value
            elif isinstance(value, (list, dict)):
                # Serialize complex types as JSON strings
                sanitized[str_key] = json.dumps(value)
            else:
                sanitized[str_key] = str(value)
        
        return sanitized
    
    def store_embeddings(
        self, 
        embedded_chunks: List[Dict[str, Any]], 
        collection_name: str, 
        batch_size: Optional[int] = None,
        clear_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Store embeddings in ChromaDB with batch processing and error recovery.
        
        Args:
            embedded_chunks: List of chunks with embeddings
            collection_name: Name of the collection to store in
            batch_size: Batch size for processing (defaults to config value)
            clear_existing: Whether to clear existing collection data (default: True)
            
        Returns:
            Storage statistics dictionary
            
        Raises:
            ValidationError: If no chunks provided or collection_name is empty
            VectorStoreError: If storage fails completely
        """
        from ..utils.exceptions import ValidationError, VectorStoreError
        
        if not embedded_chunks:
            logger.info("No embedded chunks to store")
            return {"stored_count": 0, "collection_name": collection_name}
            
        if not collection_name:
            raise ValidationError("Collection name cannot be empty", "collection_name", "non-empty string")
        
        batch_size = batch_size or CHROMA_BATCH_SIZE
        
        logger.info(f"🚀 Storing {len(embedded_chunks)} embeddings in ChromaDB...")
        logger.info(f"📦 Collection: {collection_name}")
        logger.info(f"📊 Batch size: {batch_size}")
        
        try:
            collection = self._get_or_create_collection(collection_name)
        except Exception as e:
            raise VectorStoreError(f"Failed to get/create collection: {e}", "create_collection", collection_name)
        
        # Optionally clear existing data in collection
        if clear_existing:
            try:
                # Delete the collection if it has data
                if collection.count() > 0:
                    safe_name = sanitize_collection_name(collection_name)
                    self.client.delete_collection(name=safe_name)
                    logger.info("🗑️  Deleted existing collection with data")
                    # Recreate the collection
                    collection = self._get_or_create_collection(collection_name)
                    logger.info("📦 Created fresh collection")
            except Exception as e:
                logger.warning(f"Could not clear existing collection data: {e}")
                # Continue anyway - might be empty collection
        
        # Process in batches, continue on failures
        total_batches = (len(embedded_chunks) + batch_size - 1) // batch_size
        progress = ProgressTracker(total_batches, "Storing embeddings")
        stored_count = 0
        failed_batches = []
        
        for batch_idx in range(0, len(embedded_chunks), batch_size):
            batch_end = min(batch_idx + batch_size, len(embedded_chunks))
            batch_chunks = embedded_chunks[batch_idx:batch_end]
            batch_num = batch_idx // batch_size + 1
            
            try:
                ids, embeddings, metadatas, documents = self._prepare_batch_data(batch_chunks)
                
                collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents
                )
                
                stored_count += len(batch_chunks)
                progress.update()
                
            except Exception as e:
                # Log batch failure and continue with other batches
                logger.warning(f"Batch {batch_num}/{total_batches} failed, skipping {len(batch_chunks)} chunks: {e}")
                failed_batches.append(batch_num)
                progress.update()
                continue
        
        progress.finish()
        
        # Check if any data was stored
        if stored_count == 0:
            raise VectorStoreError("All batches failed - no embeddings stored", "store", collection_name)
        
        # Get final collection count
        try:
            collection_count = collection.count()
        except Exception as e:
            logger.warning(f"Could not get collection count: {e}")
            collection_count = stored_count  # Use our count as fallback
        
        # Report results
        if failed_batches:
            logger.warning(f"Failed to store {len(failed_batches)} batches: {failed_batches}")
        
        stats = {
            "stored_count": stored_count,
            "collection_name": sanitize_collection_name(collection_name),
            "collection_count": collection_count,
            "failed_batches": len(failed_batches),
            "success_rate": f"{((total_batches - len(failed_batches)) / total_batches * 100):.1f}%",
            "using_server": self.using_server
        }
        
        # Only include db_path when using local persistence
        if not self.using_server:
            stats["db_path"] = self.db_path
        
        logger.info(f"✅ Successfully stored {stored_count} embeddings")
        logger.info(f"📊 Collection now contains {collection_count} items")
        if failed_batches:
            logger.warning(f"⚠️  {len(failed_batches)} batches failed out of {total_batches}")
        
        return stats
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about a collection with error recovery.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection information dictionary
        """
        from ..utils.exceptions import VectorStoreError
        
        if not self.client:
            raise VectorStoreError("ChromaDB client not initialized", "get_info")
            
        try:
            safe_name = sanitize_collection_name(collection_name)
            collection = self.client.get_collection(name=safe_name)
            
            return {
                "name": safe_name,
                "count": collection.count(),
                "metadata": collection.metadata,
                "exists": True
            }
        except Exception as e:
            # Collection doesn't exist or other error
            logger.debug(f"Collection info error for '{collection_name}': {e}")
            return {
                "name": sanitize_collection_name(collection_name), 
                "count": 0, 
                "exists": False,
                "error": str(e)
            }
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections in the database with error recovery.
        
        Returns:
            List of collection information dictionaries
        """
        from ..utils.exceptions import VectorStoreError
        
        if not self.client:
            raise VectorStoreError("ChromaDB client not initialized", "list_collections")
            
        try:
            collections = self.client.list_collections()
            result = []
            
            # Continue processing even if individual collections fail
            for col in collections:
                try:
                    result.append({
                        "name": col.name,
                        "count": col.count(),
                        "metadata": col.metadata
                    })
                except Exception as e:
                    logger.warning(f"Error getting info for collection '{col.name}': {e}")
                    # Add partial info
                    result.append({
                        "name": col.name,
                        "count": -1,  # Indicates error
                        "metadata": {},
                        "error": str(e)
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []


def store_repository_embeddings(
    base_dir: Union[str, Path], 
    repo_name: str, 
    embedded_chunks: List[Dict[str, Any]], 
    collection_name: Optional[str] = None,
    custom_chromadb_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Store embeddings for a repository in ChromaDB.
    
    Args:
        base_dir: Base directory for ChromaDB storage
        repo_name: Repository name for collection naming and path construction
        embedded_chunks: List of embedded chunks to store
        collection_name: Optional custom collection name (defaults to repo_name)
    
    Returns:
        Storage statistics dictionary
        
    Raises:
        ValueError: If no embedded chunks provided or repo_name is empty
        RuntimeError: If storage fails
    """
    if not embedded_chunks:
        raise ValueError("No embedded chunks provided")
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
    
    if not collection_name:
        collection_name = repo_name
    
    vector_store = ChromaVectorStore(base_dir=base_dir, repo_name=repo_name, custom_chromadb_dir=custom_chromadb_dir)
    stats = vector_store.store_embeddings(embedded_chunks, collection_name)
    
    return stats


def get_repository_collection_info(
    repo_name: str, 
    collection_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get information about a repository's collection.
    
    Args:
        repo_name: Repository name (used as default collection name)
        collection_name: Optional custom collection name
    
    Returns:
        Collection information dictionary
        
    Raises:
        ValueError: If repo_name is empty
    """
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    if not collection_name:
        collection_name = repo_name
    
    vector_store = ChromaVectorStore()
    return vector_store.get_collection_info(collection_name)


__all__ = [
    'ChromaVectorStore',
    'get_repository_collection_info',
    'store_repository_embeddings',
]
