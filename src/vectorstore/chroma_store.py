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
    CHROMA_SERVER_AUTH_TOKEN,
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
        repo_name: Optional[str] = None
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
            self.db_path = str(get_storage_path(base_dir, 'chromadb', repo_name))
        else:
            # Fallback to current directory if nothing provided
            self.db_path = str(Path.cwd() / CHROMA_DB_DIR / 'default')
        
        self.client: Optional[chromadb.Client] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """
        Initialize ChromaDB client with fallback from server to local.
        
        Raises:
            RuntimeError: If both server and local client initialization fail
        """
        try:
            if USE_CHROMA_SERVER:
                logger.info(f"Connecting to ChromaDB server at: {CHROMA_SERVER_URL}")
                self.client = chromadb.HttpClient(host="localhost", port=8000)
                
                try:
                    self.client.heartbeat()
                    logger.info("ChromaDB server connection successful")
                    return
                except Exception as e:
                    logger.error(f"ChromaDB server connection failed: {str(e)}")
                    logger.info("🔄 Falling back to local persistence...")
                    raise e
            else:
                self._initialize_local_client()
                
        except Exception as e:
            if USE_CHROMA_SERVER:
                logger.info("🔄 Server connection failed, using local persistence...")
                try:
                    self._initialize_local_client()
                except Exception as fallback_e:
                    raise RuntimeError(f"Failed to initialize ChromaDB client: {str(fallback_e)}")
            else:
                raise RuntimeError(f"Failed to initialize ChromaDB client: {str(e)}")
    
    def _initialize_local_client(self) -> None:
        """Initialize local ChromaDB client with persistence."""
        os.makedirs(self.db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        logger.info(f"ChromaDB local persistence at: {self.db_path}")
    
    def _get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        """
        Get or create a collection for the repository.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaDB collection instance
            
        Raises:
            RuntimeError: If collection creation/retrieval fails
        """
        if not self.client:
            raise RuntimeError("ChromaDB client not initialized")
            
        try:
            safe_name = sanitize_collection_name(collection_name)
            
            try:
                collection = self.client.get_collection(name=safe_name)
                logger.info(f"Using existing collection: {safe_name}")
                return collection
            except Exception:
                collection = self.client.create_collection(
                    name=safe_name,
                    metadata={"description": f"Code chunks for repository: {collection_name}"}
                )
                logger.info(f"Created new collection: {safe_name}")
                return collection
                
        except Exception as e:
            raise RuntimeError(f"Failed to get/create collection '{collection_name}': {str(e)}")
    
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
            # Generate unique ID for chunk
            chunk_id = f"chunk_{i}_{hash(chunk.get('content', ''))}"
            ids.append(chunk_id)
            
            # Extract embedding
            embedding = chunk.get('embedding')
            if not embedding:
                raise ValueError(f"Chunk at index {i} missing embedding")
            embeddings.append(embedding)
            
            # Prepare metadata (exclude embedding to avoid duplication)
            metadata = {k: v for k, v in chunk.items() if k != 'embedding'}
            metadata = self._sanitize_metadata(metadata)
            metadatas.append(metadata)
            
            # Extract document content
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
        batch_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Store embeddings in ChromaDB with batch processing.
        
        Args:
            embedded_chunks: List of chunks with embeddings
            collection_name: Name of the collection to store in
            batch_size: Batch size for processing (defaults to config value)
            
        Returns:
            Storage statistics dictionary
            
        Raises:
            ValueError: If no chunks provided
            RuntimeError: If storage fails
        """
        if not embedded_chunks:
            logger.info("No embedded chunks to store")
            return {"stored_count": 0, "collection_name": collection_name}
        
        batch_size = batch_size or CHROMA_BATCH_SIZE
        
        logger.info(f"🚀 Storing {len(embedded_chunks)} embeddings in ChromaDB...")
        logger.info(f"📦 Collection: {collection_name}")
        logger.info(f"📊 Batch size: {batch_size}")
        
        collection = self._get_or_create_collection(collection_name)
        
        # Clear existing data in collection
        try:
            collection.delete()
            logger.info("🗑️  Cleared existing data in collection")
        except Exception:
            # Collection might be empty, continue
            pass
        
        # Process in batches
        total_batches = (len(embedded_chunks) + batch_size - 1) // batch_size
        progress = ProgressTracker(total_batches, "Storing embeddings")
        stored_count = 0
        
        for batch_idx in range(0, len(embedded_chunks), batch_size):
            batch_end = min(batch_idx + batch_size, len(embedded_chunks))
            batch_chunks = embedded_chunks[batch_idx:batch_end]
            
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
                progress.finish()
                raise RuntimeError(f"Failed to store batch {batch_idx//batch_size + 1}: {str(e)}")
        
        progress.finish()
        
        # Get final collection count
        collection_count = collection.count()
        
        stats = {
            "stored_count": stored_count,
            "collection_name": sanitize_collection_name(collection_name),
            "collection_count": collection_count,
            "db_path": self.db_path
        }
        
        logger.info(f"✅ Successfully stored {stored_count} embeddings")
        logger.info(f"📊 Collection now contains {collection_count} items")
        
        return stats
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection information dictionary
        """
        if not self.client:
            raise RuntimeError("ChromaDB client not initialized")
            
        try:
            safe_name = sanitize_collection_name(collection_name)
            collection = self.client.get_collection(name=safe_name)
            
            return {
                "name": safe_name,
                "count": collection.count(),
                "metadata": collection.metadata,
                "exists": True
            }
        except ValueError:
            return {
                "name": sanitize_collection_name(collection_name), 
                "count": 0, 
                "exists": False
            }
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections in the database.
        
        Returns:
            List of collection information dictionaries
        """
        if not self.client:
            raise RuntimeError("ChromaDB client not initialized")
            
        try:
            collections = self.client.list_collections()
            return [
                {
                    "name": col.name,
                    "count": col.count(),
                    "metadata": col.metadata
                }
                for col in collections
            ]
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return []


def store_repository_embeddings(
    base_dir: Union[str, Path], 
    repo_name: str, 
    embedded_chunks: List[Dict[str, Any]], 
    collection_name: Optional[str] = None
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
    
    vector_store = ChromaVectorStore(base_dir=base_dir, repo_name=repo_name)
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
