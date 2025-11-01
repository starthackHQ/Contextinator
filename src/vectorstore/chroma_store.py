import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from ..utils import ProgressTracker, logger
from ..config import (
    CHROMA_DB_DIR,
    CHROMA_SERVER_URL, 
    CHROMA_SERVER_AUTH_TOKEN, 
    USE_CHROMA_SERVER,
    CHROMA_BATCH_SIZE,
    sanitize_collection_name,
    get_storage_path
)


class ChromaVectorStore:
    """ChromaDB vector store for semantic code search."""
    
    def __init__(self, db_path: Optional[str] = None, base_dir: Optional[str] = None, repo_name: Optional[str] = None):
        """
        Initialize ChromaDB vector store.
        
        Args:
            db_path: Explicit path to ChromaDB database (overrides base_dir/repo_name)
            base_dir: Base directory for relative path construction
            repo_name: Repository name for path construction
        """
        if db_path:
            self.db_path = db_path
        elif base_dir and repo_name:
            self.db_path = str(get_storage_path(base_dir, 'chromadb', repo_name))
        else:
            # Fallback to current directory if nothing provided
            from pathlib import Path
            self.db_path = str(Path.cwd() / CHROMA_DB_DIR / 'default')
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client."""
        try:
            if USE_CHROMA_SERVER:
                logger.info(f"Connecting to ChromaDB server at: {CHROMA_SERVER_URL}")
                self.client = chromadb.HttpClient(host="localhost", port=8000)
                
                try:
                    self.client.heartbeat()
                    logger.info("ChromaDB server connection successful")
                except Exception as e:
                    logger.error(f"ChromaDB server connection failed: {str(e)}")
                    logger.info("🔄 Falling back to local persistence...")
                    raise e
            else:
                os.makedirs(self.db_path, exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=self.db_path,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                logger.info(f"ChromaDB local persistence at: {self.db_path}")
        except Exception as e:
            if USE_CHROMA_SERVER:
                logger.info("🔄 Server connection failed, using local persistence...")
                try:
                    os.makedirs(self.db_path, exist_ok=True)
                    self.client = chromadb.PersistentClient(
                        path=self.db_path,
                        settings=Settings(
                            anonymized_telemetry=False,
                            allow_reset=True
                        )
                    )
                    logger.info(f"ChromaDB local persistence at: {self.db_path}")
                except Exception as fallback_e:
                    raise RuntimeError(f"Failed to initialize ChromaDB client: {str(fallback_e)}")
            else:
                raise RuntimeError(f"Failed to initialize ChromaDB client: {str(e)}")
    
    def _get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        """Get or create a collection for the repository."""
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
    
    def _prepare_batch_data(self, embedded_chunks: List[Dict[str, Any]]) -> tuple:
        """Prepare batch data for ChromaDB insertion."""
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for i, chunk in enumerate(embedded_chunks):
            chunk_id = f"chunk_{i}_{hash(chunk.get('content', ''))}"
            ids.append(chunk_id)
            
            embedding = chunk.get('embedding')
            if not embedding:
                raise ValueError(f"Chunk at index {i} missing embedding")
            embeddings.append(embedding)
            
            metadata = {k: v for k, v in chunk.items() if k != 'embedding'}
            metadata = self._sanitize_metadata(metadata)
            metadatas.append(metadata)
            
            documents.append(chunk.get('content', ''))
        
        return ids, embeddings, metadatas, documents
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata to ensure ChromaDB compatibility."""
        sanitized = {}
        
        for key, value in metadata.items():
            str_key = str(key).replace('.', '_').replace(' ', '_')
            
            if isinstance(value, (str, int, float, bool)):
                sanitized[str_key] = value
            elif isinstance(value, (list, dict)):
                sanitized[str_key] = json.dumps(value)
            else:
                sanitized[str_key] = str(value)
        
        return sanitized
    
    def store_embeddings(self, embedded_chunks: List[Dict[str, Any]], 
                        collection_name: str, batch_size: Optional[int] = None) -> Dict[str, Any]:
        """Store embeddings in ChromaDB."""
        if not embedded_chunks:
            logger.info("No embedded chunks to store")
            return {"stored_count": 0, "collection_name": collection_name}
        
        batch_size = batch_size or CHROMA_BATCH_SIZE
        
        logger.info("🚀 Storing %d embeddings in ChromaDB...", len(embedded_chunks))
        logger.info("📦 Collection: %s", collection_name)
        logger.info("📊 Batch size: %d", batch_size)
        
        collection = self._get_or_create_collection(collection_name)
        
        try:
            collection.delete()
            logger.info("🗑️  Cleared existing data in collection")
        except Exception:
            pass
        
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
        
        collection_count = collection.count()
        
        stats = {
            "stored_count": stored_count,
            "collection_name": sanitize_collection_name(collection_name),
            "collection_count": collection_count,
            "db_path": self.db_path
        }
        
        logger.info(f"Successfully stored {stored_count} embeddings")
        logger.info("📊 Collection now contains %d items", collection_count)
        
        return stats
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection."""
        try:
            safe_name = sanitize_collection_name(collection_name)
            collection = self.client.get_collection(name=safe_name)
            
            return {
                "name": safe_name,
                "count": collection.count(),
                "metadata": collection.metadata
            }
        except ValueError:
            return {"name": safe_name, "count": 0, "exists": False}
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections in the database."""
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
            logger.error("Error listing collections: %s", str(e))
            return []


def store_repository_embeddings(base_dir: str, repo_name: str, embedded_chunks: List[Dict[str, Any]], 
                               collection_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Store embeddings for a repository in ChromaDB.
    
    Args:
        base_dir: Base directory for ChromaDB storage
        repo_name: Repository name for collection naming and path construction
        embedded_chunks: List of embedded chunks to store
        collection_name: Optional custom collection name (defaults to repo_name)
    
    Returns:
        Storage statistics
    """
    if not embedded_chunks:
        raise ValueError("No embedded chunks provided")
    
    if not collection_name:
        collection_name = repo_name
    
    vector_store = ChromaVectorStore(base_dir=base_dir, repo_name=repo_name)
    stats = vector_store.store_embeddings(embedded_chunks, collection_name)
    
    return stats


def get_repository_collection_info(repo_name: str, collection_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about a repository's collection.
    
    Args:
        repo_name: Repository name (used as default collection name)
        collection_name: Optional custom collection name
    
    Returns:
        Collection information
    """
    if not collection_name:
        collection_name = repo_name
    
    vector_store = ChromaVectorStore()
    return vector_store.get_collection_info(collection_name)
