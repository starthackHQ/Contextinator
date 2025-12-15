"""Tests for ChromaDB vector store functionality."""
import pytest
from pathlib import Path
from contextinator.vectorstore.chroma_store import ChromaVectorStore


class TestChromaVectorStore:
    """Test ChromaDB vector store operations."""
    
    def test_store_initialization(self, temp_chromadb):
        """Test vector store initialization."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        assert store is not None
        assert store.client is not None
    
    def test_store_embeddings_basic(self, temp_chromadb):
        """Test basic storing of embeddings."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        embedded_chunks = [
            {
                'id': 'test_1',
                'content': 'test content',
                'embedding': [0.1] * 3072,
                'file_path': 'test.py',
                'language': 'python',
                'node_type': 'function'
            }
        ]
        
        result = store.store_embeddings(
            embedded_chunks=embedded_chunks,
            collection_name="test_collection"
        )
        
        assert 'stored_count' in result
        assert result['stored_count'] == 1
    
    def test_store_embeddings_batch(self, temp_chromadb):
        """Test storing multiple embeddings."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        embedded_chunks = [
            {
                'id': f'chunk_{i}',
                'content': f'content {i}',
                'embedding': [0.1 * i] * 3072,
                'file_path': 'test.py',
                'language': 'python',
                'node_type': 'function'
            }
            for i in range(5)
        ]
        
        result = store.store_embeddings(
            embedded_chunks=embedded_chunks,
            collection_name="test_batch"
        )
        
        assert 'stored_count' in result
        assert result['stored_count'] == 5
    
    def test_store_embeddings_clear_existing(self, temp_chromadb):
        """Test clearing existing embeddings before storing."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        # Use unique collection name to avoid conflicts with stale server data
        import uuid
        collection_name = f"test_clear_{uuid.uuid4().hex[:8]}"
        
        # Store initial data (clear_existing=True to ensure clean state)
        embedded_chunks1 = [
            {
                'id': 'chunk_1',
                'content': 'first content',
                'embedding': [0.1] * 3072,
                'file_path': 'test.py',
                'language': 'python'
            }
        ]
        
        store.store_embeddings(
            embedded_chunks=embedded_chunks1,
            collection_name=collection_name,
            clear_existing=True
        )
        
        # Verify initial data stored
        info = store.get_collection_info(collection_name)
        assert info['count'] == 1
        
        # Store new data with clear=True (should replace)
        embedded_chunks2 = [
            {
                'id': 'chunk_2',
                'content': 'second content',
                'embedding': [0.2] * 3072,
                'file_path': 'test.py',
                'language': 'python'
            }
        ]
        
        store.store_embeddings(
            embedded_chunks=embedded_chunks2,
            collection_name=collection_name,
            clear_existing=True
        )
        
        # Should only have 1 item after clear
        info = store.get_collection_info(collection_name)
        assert info['count'] == 1
    
    def test_get_collection_info(self, temp_chromadb):
        """Test retrieving collection information."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        embedded_chunks = [
            {
                'id': 'test_1',
                'content': 'test',
                'embedding': [0.1] * 3072,
                'file_path': 'test.py',
                'language': 'python'
            }
        ]
        
        store.store_embeddings(
            embedded_chunks=embedded_chunks,
            collection_name="info_test"
        )
        
        info = store.get_collection_info("info_test")
        
        assert 'name' in info
        assert 'count' in info
        assert info['count'] == 1
    
    def test_list_collections(self, temp_chromadb):
        """Test listing all collections."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        # Create some collections
        for i in range(3):
            embedded_chunks = [
                {
                    'id': f'chunk_{i}',
                    'content': f'content {i}',
                    'embedding': [0.1] * 3072,
                    'file_path': 'test.py',
                    'language': 'python'
                }
            ]
            store.store_embeddings(
                embedded_chunks=embedded_chunks,
                collection_name=f"collection_{i}"
            )
        
        collections = store.list_collections()
        assert len(collections) >= 3
        assert all('name' in c for c in collections)
        assert all('count' in c for c in collections)
    
    def test_metadata_sanitization(self, temp_chromadb):
        """Test that complex metadata is properly sanitized."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        embedded_chunks = [
            {
                'id': 'test_1',
                'content': 'test content',
                'embedding': [0.1] * 3072,
                'file_path': 'test.py',
                'language': 'python',
                'node_type': 'function',
                'complex_data': {'nested': 'value'},
                'list_data': [1, 2, 3] 
            }
        ]
        
        result = store.store_embeddings(
            embedded_chunks=embedded_chunks,
            collection_name="sanitize_test"
        )
        
        assert 'stored_count' in result
        assert result['stored_count'] == 1
    
    def test_empty_embeddings_list(self, temp_chromadb):
        """Test handling of empty embeddings list."""
        client, temp_dir = temp_chromadb
        store = ChromaVectorStore(db_path=temp_dir)
        
        result = store.store_embeddings(
            embedded_chunks=[],
            collection_name="empty_test"
        )
        
        assert 'stored_count' in result
        assert result['stored_count'] == 0
