import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from .utils import ProgressTracker
from .config import CHROMA_DB_PATH, CHROMA_SERVER_URL, CHROMA_SERVER_AUTH_TOKEN, sanitize_collection_name


class ChromaVectorStore:
    """ChromaDB vector store for semantic code search."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize ChromaDB vector store.
        
        Args:
            db_path: Optional custom database path
        """
        self.db_path = db_path or CHROMA_DB_PATH
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client."""
        try:
            use_server = os.getenv('USE_CHROMA_SERVER', 'true').lower() == 'true'
            
            if use_server:
                print(f"🗄️  Connecting to ChromaDB server at: {CHROMA_SERVER_URL}")
                
                # Simple HTTP client initialization
                self.client = chromadb.HttpClient(host="localhost", port=8000)
                
                # Test connection
                try:
                    self.client.heartbeat()
                    print(f"✅ ChromaDB server connection successful")
                except Exception as e:
                    print(f"❌ ChromaDB server connection failed: {str(e)}")
                    print("🔄 Falling back to local persistence...")
                    raise e
                
            else:
                # Use local persistent client
                os.makedirs(self.db_path, exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=self.db_path,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                print(f"🗄️  ChromaDB local persistence at: {self.db_path}")
            
        except Exception as e:
            # Fallback to local if server fails
            if use_server:
                print("🔄 Server connection failed, using local persistence...")
                try:
                    os.makedirs(self.db_path, exist_ok=True)
                    self.client = chromadb.PersistentClient(
                        path=self.db_path,
                        settings=Settings(
                            anonymized_telemetry=False,
                            allow_reset=True
                        )
                    )
                    print(f"🗄️  ChromaDB local persistence at: {self.db_path}")
                except Exception as fallback_e:
                    raise RuntimeError(f"Failed to initialize ChromaDB client: {str(fallback_e)}")
            else:
                raise RuntimeError(f"Failed to initialize ChromaDB client: {str(e)}")
    
    def _get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        """
        Get or create a collection for the repository.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaDB collection object
        """
        try:
            safe_name = sanitize_collection_name(collection_name)
            
            try:
                collection = self.client.get_collection(name=safe_name)
                print(f"📚 Using existing collection: {safe_name}")
                return collection
            except Exception:
                
                collection = self.client.create_collection(
                    name=safe_name,
                    metadata={"description": f"Code chunks for repository: {collection_name}"}
                )
                print(f"📚 Created new collection: {safe_name}")
                return collection
                
        except Exception as e:
            raise RuntimeError(f"Failed to get/create collection '{collection_name}': {str(e)}")
    
    def _prepare_batch_data(self, embedded_chunks: List[Dict[str, Any]]) -> tuple:
        """
        Prepare batch data for ChromaDB insertion.
        
        Args:
            embedded_chunks: List of chunks with embeddings
            
        Returns:
            Tuple of (ids, embeddings, metadatas, documents)
        """
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for i, chunk in enumerate(embedded_chunks):
            chunk_id = f"chunk_{i}_{hash(chunk.get('content', ''))}"
            ids.append(chunk_id)
            
            # Extract embedding
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
        """
        Sanitize metadata to ensure ChromaDB compatibility.
        
        Args:
            metadata: Original metadata dictionary
            
        Returns:
            Sanitized metadata dictionary
        """
        sanitized = {}
        
        for key, value in metadata.items():
            # Convert key to string and ensure it's valid
            str_key = str(key).replace('.', '_').replace(' ', '_')
            
            # Handle different value types
            if isinstance(value, (str, int, float, bool)):
                sanitized[str_key] = value
            elif isinstance(value, (list, dict)):
                # Convert complex types to JSON strings
                sanitized[str_key] = json.dumps(value)
            else:
                # Convert other types to string
                sanitized[str_key] = str(value)
        
        return sanitized
    
    def store_embeddings(self, embedded_chunks: List[Dict[str, Any]], 
                        collection_name: str, batch_size: int = 100) -> Dict[str, Any]:
        """
        Store embeddings in ChromaDB.
        
        Args:
            embedded_chunks: List of chunks with embeddings
            collection_name: Name of the collection
            batch_size: Batch size for insertion
            
        Returns:
            Dictionary with storage statistics
        """
        if not embedded_chunks:
            print("No embedded chunks to store")
            return {"stored_count": 0, "collection_name": collection_name}
        
        print(f"🚀 Storing {len(embedded_chunks)} embeddings in ChromaDB...")
        print(f"📦 Collection: {collection_name}")
        print(f"📊 Batch size: {batch_size}")
        
        # Get or create collection
        collection = self._get_or_create_collection(collection_name)
        
        # Clear existing data in collection (optional - you might want to append instead)
        try:
            collection.delete()  # Delete all existing data
            print("🗑️  Cleared existing data in collection")
        except Exception:
            pass  # Collection might be empty
        
        # Process chunks in batches
        total_batches = (len(embedded_chunks) + batch_size - 1) // batch_size
        progress = ProgressTracker(total_batches, "Storing embeddings")
        stored_count = 0
        
        for batch_idx in range(0, len(embedded_chunks), batch_size):
            batch_end = min(batch_idx + batch_size, len(embedded_chunks))
            batch_chunks = embedded_chunks[batch_idx:batch_end]
            
            try:
                # Prepare batch data
                ids, embeddings, metadatas, documents = self._prepare_batch_data(batch_chunks)
                
                # Insert batch into ChromaDB
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
        
        # Get final collection stats
        collection_count = collection.count()
        
        stats = {
            "stored_count": stored_count,
            "collection_name": sanitize_collection_name(collection_name),
            "collection_count": collection_count,
            "db_path": self.db_path
        }
        
        print(f"✅ Successfully stored {stored_count} embeddings")
        print(f"📊 Collection now contains {collection_count} items")
        
        return stats
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection information
        """
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
        """
        List all collections in the database.
        
        Returns:
            List of collection information dictionaries
        """
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
            print(f"Error listing collections: {str(e)}")
            return []


def store_repository_embeddings(repo_path: str, embedded_chunks: List[Dict[str, Any]], 
                               collection_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Store embeddings for a repository in ChromaDB.
    
    Args:
        repo_path: Path to the repository
        embedded_chunks: List of chunks with embeddings
        collection_name: Optional collection name (defaults to repo name)
        
    Returns:
        Dictionary with storage statistics
    """
    if not embedded_chunks:
        raise ValueError("No embedded chunks provided")
    
    # Determine collection name
    if not collection_name:
        repo_name = Path(repo_path).name
        collection_name = repo_name
    
    # Initialize vector store
    vector_store = ChromaVectorStore()
    
    # Store embeddings
    stats = vector_store.store_embeddings(embedded_chunks, collection_name)
    
    return stats


def get_repository_collection_info(repo_path: str, collection_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about a repository's collection.
    
    Args:
        repo_path: Path to the repository
        collection_name: Optional collection name (defaults to repo name)
        
    Returns:
        Dictionary with collection information
    """
    # Determine collection name
    if not collection_name:
        repo_name = Path(repo_path).name
        collection_name = repo_name
    

    vector_store = ChromaVectorStore()
    
    # Get collection info
    return vector_store.get_collection_info(collection_name)
