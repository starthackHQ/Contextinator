"""Integration tests for full pipeline."""
import pytest
from pathlib import Path
from contextinator.chunking.chunk_service import chunk_repository
from contextinator.vectorstore.chroma_store import ChromaVectorStore
from contextinator.tools.semantic_search import semantic_search
from contextinator.tools.symbol_search import symbol_search


@pytest.mark.integration
def test_full_chunking_pipeline(temp_repo, temp_chromadb):
    """Test complete chunking and storage pipeline."""
    client, chromadb_dir = temp_chromadb
    
    # Step 1: Chunk the repository
    print("\n[Step 1] Chunking repository...")
    chunks = chunk_repository(temp_repo, save=False)
    
    assert len(chunks) > 0, "Should have chunked at least one code block"
    assert all('chunk_id' in chunk for chunk in chunks), "All chunks should have IDs"
    assert all('content' in chunk for chunk in chunks), "All chunks should have content"
    print(f"✓ Chunked {len(chunks)} code blocks")
    
    print("\n✅ Chunking pipeline test passed!")


@pytest.mark.integration
def test_chunk_and_store(temp_repo, temp_chromadb, sample_embedded_chunks):
    """Test chunking and storing."""
    client, chromadb_dir = temp_chromadb
    store = ChromaVectorStore(db_path=chromadb_dir)
    
    # Store pre-embedded chunks
    store.add_chunks("test_store", sample_embedded_chunks)
    
    collection = store.get_or_create_collection("test_store")
    assert collection.count() == len(sample_embedded_chunks)


@pytest.mark.integration
def test_multiple_collections(temp_chromadb, sample_embedded_chunks):
    """Test managing multiple collections simultaneously."""
    client, chromadb_dir = temp_chromadb
    store = ChromaVectorStore(db_path=chromadb_dir)
    
    # Create multiple collections
    store.add_chunks("repo1", sample_embedded_chunks[:1])
    store.add_chunks("repo2", sample_embedded_chunks[1:])
    
    # Verify both collections exist
    collections = store.list_collections()
    collection_names = [c.name for c in collections]
    
    assert "repo1" in collection_names
    assert "repo2" in collection_names
    
    # Verify correct counts
    repo1_count = store.get_or_create_collection("repo1").count()
    repo2_count = store.get_or_create_collection("repo2").count()
    
    assert repo1_count == 1
    assert repo2_count == 1


@pytest.mark.integration
def test_persistence(temp_chromadb, sample_embedded_chunks):
    """Test that data persists across ChromaDB client restarts."""
    client, chromadb_dir = temp_chromadb
    
    # Store data with first client
    store1 = ChromaVectorStore(db_path=chromadb_dir)
    store1.add_chunks("persist_test", sample_embedded_chunks)
    initial_count = store1.get_or_create_collection("persist_test").count()
    
    # Create new store instance (simulating restart)
    store2 = ChromaVectorStore(db_path=chromadb_dir)
    collection = store2.get_or_create_collection("persist_test")
    
    # Data should still be there
    assert collection.count() == initial_count
    
    # Should be able to query
    results = collection.get(ids=[sample_embedded_chunks[0]['chunk_id']])
    assert len(results['ids']) == 1
