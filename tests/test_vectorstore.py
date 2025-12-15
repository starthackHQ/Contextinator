"""Tests for vector store functionality."""
import pytest
from pathlib import Path
from contextinator.vectorstore.chroma_store import ChromaVectorStore


class TestChromaVectorStore:
    """Test ChromaDB vector store functionality."""
    
    def test_initialization(self, temp_chromadb):
        """Test ChromaDB store initialization."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        assert store is not None
        assert store.db_path == temp_dir
        assert store.client is not None
    
    def test_create_collection(self, temp_chromadb):
        """Test creating a new collection."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        collection = store.get_or_create_collection("test_collection")
        
        assert collection is not None
        assert collection.name == "test_collection"
    
    def test_collection_name_sanitization(self, temp_chromadb):
        """Test that collection names are properly sanitized."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        # Test various invalid characters
        collection = store.get_or_create_collection("Test-Repo@123")
        
        assert collection is not None
        # Name should be sanitized (no special chars)
        assert collection.name.replace("_", "").replace("-", "").isalnum()
    
    def test_add_embeddings(self, temp_chromadb, sample_embedded_chunks):
        """Test adding embeddings to collection."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        store.add_chunks("test_repo", sample_embedded_chunks)
        
        collection = store.get_or_create_collection("test_repo")
        assert collection.count() == len(sample_embedded_chunks)
    
    def test_add_duplicate_chunks(self, temp_chromadb, sample_embedded_chunks):
        """Test handling of duplicate chunk IDs."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        # Add chunks twice
        store.add_chunks("test_repo", sample_embedded_chunks)
        store.add_chunks("test_repo", sample_embedded_chunks)
        
        collection = store.get_or_create_collection("test_repo")
        # Should either update or deduplicate
        assert collection.count() <= len(sample_embedded_chunks) * 2
    
    def test_query_collection(self, test_collection):
        """Test querying a collection."""
        collection, temp_dir = test_collection
        
        # Query with embedding
        results = collection.query(
            query_embeddings=[[0.15] * 1536],
            n_results=2
        )
        
        assert results is not None
        assert 'ids' in results
        assert len(results['ids'][0]) <= 2
    
    def test_get_by_metadata(self, test_collection):
        """Test retrieving chunks by metadata filters."""
        collection, temp_dir = test_collection
        
        # Query for specific file
        results = collection.get(
            where={"file_path": "src/main.py"}
        )
        
        assert results is not None
        assert 'ids' in results
        assert len(results['ids']) >= 1
    
    def test_delete_collection(self, temp_chromadb):
        """Test deleting a collection."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        # Create and delete collection
        store.get_or_create_collection("temp_collection")
        store.delete_collection("temp_collection")
        
        # Verify deletion
        collections = client.list_collections()
        collection_names = [c.name for c in collections]
        assert "temp_collection" not in collection_names
    
    def test_list_collections(self, temp_chromadb):
        """Test listing all collections."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        # Create multiple collections
        store.get_or_create_collection("repo1")
        store.get_or_create_collection("repo2")
        
        collections = store.list_collections()
        
        assert len(collections) >= 2
        collection_names = [c.name for c in collections]
        assert "repo1" in collection_names
        assert "repo2" in collection_names
    
    def test_collection_metadata(self, temp_chromadb):
        """Test adding metadata to collections."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        metadata = {
            "description": "Test repository",
            "version": "1.0",
            "language": "python"
        }
        
        collection = store.get_or_create_collection(
            "test_repo",
            metadata=metadata
        )
        
        assert collection.metadata is not None
    
    def test_reset_collection(self, temp_chromadb, sample_embedded_chunks):
        """Test resetting/clearing a collection."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        # Add chunks
        store.add_chunks("test_repo", sample_embedded_chunks)
        collection = store.get_or_create_collection("test_repo")
        initial_count = collection.count()
        
        # Reset collection
        store.delete_collection("test_repo")
        new_collection = store.get_or_create_collection("test_repo")
        
        assert new_collection.count() == 0
        assert initial_count > 0
    
    def test_update_chunk(self, temp_chromadb, sample_embedded_chunks):
        """Test updating an existing chunk."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        # Add initial chunks
        store.add_chunks("test_repo", sample_embedded_chunks)
        
        # Update a chunk
        updated_chunk = sample_embedded_chunks[0].copy()
        updated_chunk['content'] = "# Updated content"
        
        store.add_chunks("test_repo", [updated_chunk])
        
        collection = store.get_or_create_collection("test_repo")
        assert collection.count() >= 1


class TestVectorStoreIntegration:
    """Test vector store integration with other components."""
    
    def test_store_and_retrieve(self, temp_chromadb, sample_embedded_chunks):
        """Test storing and retrieving chunks."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        # Store chunks
        store.add_chunks("integration_test", sample_embedded_chunks)
        
        # Retrieve
        collection = store.get_or_create_collection("integration_test")
        results = collection.get(
            ids=[sample_embedded_chunks[0]['chunk_id']]
        )
        
        assert len(results['ids']) == 1
        assert results['ids'][0] == sample_embedded_chunks[0]['chunk_id']
    
    def test_similarity_search(self, test_collection):
        """Test similarity-based search."""
        collection, temp_dir = test_collection
        
        # Search for authentication-related code
        results = collection.query(
            query_embeddings=[[0.1] * 1536],  # Similar to authenticate_user embedding
            n_results=3
        )
        
        assert len(results['ids'][0]) <= 3
        assert len(results['distances'][0]) <= 3
