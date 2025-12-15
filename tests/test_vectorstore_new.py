"""Tests for ChromaDB vector store."""
import pytest
from pathlib import Path


class TestChromaVectorStore:
    """Test ChromaDB vector store operations."""
    
    def test_init_local(self, temp_chromadb):
        """Test initializing local ChromaDB client."""
        from contextinator.vectorstore.chroma_store import ChromaVectorStore
        
        _, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        assert store.client is not None
        assert store.db_path == temp_dir
    
    def test_store_embeddings(self, temp_chromadb, sample_embedded_chunks):
        """Test storing embeddings."""
        from contextinator.vectorstore.chroma_store import ChromaVectorStore
        
        _, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        result = store.store_embeddings(
            sample_embedded_chunks,
            collection_name="test_collection"
        )
        
        assert result is not None
        assert "collection_name" in result or "status" in result
    
    def test_store_embeddings_with_batch_size(self, temp_chromadb, sample_embedded_chunks):
        """Test storing embeddings with custom batch size."""
        from contextinator.vectorstore.chroma_store import ChromaVectorStore
        
        _, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        result = store.store_embeddings(
            sample_embedded_chunks,
            collection_name="test_batch",
            batch_size=1
        )
        
        assert result is not None
    
    def test_get_collection_info(self, test_collection):
        """Test getting collection information."""
        store, _ = test_collection
        
        info = store.get_collection_info("test_repo")
        
        assert info is not None
        assert "count" in info or "name" in info
    
    def test_list_collections(self, test_collection):
        """Test listing all collections."""
        store, _ = test_collection
        
        collections = store.list_collections()
        
        assert isinstance(collections, list)
        assert len(collections) > 0
    
    def test_clear_existing(self, temp_chromadb, sample_embedded_chunks):
        """Test clearing existing collection data."""
        from contextinator.vectorstore.chroma_store import ChromaVectorStore
        
        _, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        # Store initial data
        store.store_embeddings(
            sample_embedded_chunks,
            collection_name="test_clear"
        )
        
        # Store again with clear_existing=True
        result = store.store_embeddings(
            sample_embedded_chunks[:1],
            collection_name="test_clear",
            clear_existing=True
        )
        
        assert result is not None
