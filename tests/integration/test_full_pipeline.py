"""Integration tests for full pipeline."""
import pytest
from pathlib import Path
from contextinator.chunking.chunk_service import chunk_repository
from contextinator.vectorstore.chroma_store import ChromaVectorStore


@pytest.mark.integration
def test_full_chunking_pipeline(temp_repo):
    """Test complete chunking pipeline."""
    # Step 1: Chunk the repository
    print("\n[Step 1] Chunking repository...")
    chunks = chunk_repository(temp_repo, save=False)
    
    assert len(chunks) > 0, "Should have chunked at least one code block"
    assert all('id' in chunk for chunk in chunks), "All chunks should have IDs"
    assert all('content' in chunk for chunk in chunks), "All chunks should have content"
    print(f"✓ Chunked {len(chunks)} code blocks")
    
    print("\n✅ Chunking pipeline test passed!")


@pytest.mark.integration
def test_chunk_and_store(temp_repo, temp_chromadb):
    """Test chunking and storing with mock embeddings."""
    client, chromadb_dir = temp_chromadb
    
    # Chunk the repository
    chunks = chunk_repository(temp_repo, save=False)
    assert len(chunks) > 0
    
    # Create mock embedded chunks
    embedded_chunks = []
    for chunk in chunks[:3]:  # Just test with first 3 chunks
        embedded_chunks.append({
            'id': chunk['id'],
            'content': chunk['content'],
            'embedding': [0.1] * 3072,  # Mock embedding
            'file_path': str(chunk.get('file_path', 'unknown')),
            'language': chunk.get('language', 'python'),
            'node_type': chunk.get('node_type', 'unknown')
        })
    
    # Store in ChromaDB
    store = ChromaVectorStore(db_path=chromadb_dir)
    result = store.store_embeddings(
        embedded_chunks=embedded_chunks,
        collection_name="test_integration"
    )
    
    assert result['stored_count'] == len(embedded_chunks)
    
    # Verify collection info
    info = store.get_collection_info("test_integration")
    assert info['count'] == len(embedded_chunks)


@pytest.mark.integration
def test_multiple_collections(temp_chromadb):
    """Test managing multiple collections simultaneously."""
    client, chromadb_dir = temp_chromadb
    store = ChromaVectorStore(db_path=chromadb_dir)
    
    # Create mock data for two collections
    chunks1 = [
        {
            'id': 'chunk_1',
            'content': 'content 1',
            'embedding': [0.1] * 3072,
            'file_path': 'test1.py',
            'language': 'python'
        }
    ]
    
    chunks2 = [
        {
            'id': 'chunk_2',
            'content': 'content 2',
            'embedding': [0.2] * 3072,
            'file_path': 'test2.py',
            'language': 'python'
        }
    ]
    
    # Store in different collections
    store.store_embeddings(chunks1, "repo1")
    store.store_embeddings(chunks2, "repo2")
    
    # Verify both collections exist
    collections = store.list_collections()
    collection_names = [c['name'] for c in collections]
    
    assert "repo1" in collection_names
    assert "repo2" in collection_names
    
    # Verify correct counts
    info1 = store.get_collection_info("repo1")
    info2 = store.get_collection_info("repo2")
    
    assert info1['count'] == 1
    assert info2['count'] == 1


@pytest.mark.integration
def test_persistence(temp_chromadb):
    """Test that data persists across ChromaDB client restarts."""
    client, chromadb_dir = temp_chromadb
    
    # Store data with first store instance
    store1 = ChromaVectorStore(db_path=chromadb_dir)
    
    chunks = [
        {
            'id': 'persist_1',
            'content': 'persistent content',
            'embedding': [0.1] * 3072,
            'file_path': 'test.py',
            'language': 'python'
        }
    ]
    
    store1.store_embeddings(chunks, "persist_test")
    initial_info = store1.get_collection_info("persist_test")
    initial_count = initial_info['count']
    
    # Create new store instance (simulating restart)
    store2 = ChromaVectorStore(db_path=chromadb_dir)
    new_info = store2.get_collection_info("persist_test")
    
    # Data should still be there
    assert new_info['count'] == initial_count
