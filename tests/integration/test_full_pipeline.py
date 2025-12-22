"""Integration tests for full pipeline."""
import pytest
import os
from pathlib import Path
from contextinator.chunking.chunk_service import chunk_repository
from contextinator.embedding.embedding_service import EmbeddingService
from contextinator.vectorstore.chroma_store import ChromaVectorStore
from contextinator.tools.semantic_search import semantic_search
from contextinator.tools.symbol_search import symbol_search


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
@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="Requires OPENAI_API_KEY for real embeddings")
async def test_complete_e2e_pipeline_with_real_embeddings(temp_repo, temp_chromadb):
    """
    Test COMPLETE end-to-end flow with REAL embeddings:
    1. Chunk repository
    2. Generate real OpenAI embeddings
    3. Store in ChromaDB
    4. Perform semantic search
    5. Perform symbol search
    """
    client, chromadb_dir = temp_chromadb
    
    print("\n" + "="*60)
    print("TESTING COMPLETE END-TO-END PIPELINE")
    print("="*60)
    
    # Step 1: Chunk the repository
    print("\n[Step 1/5] Chunking repository...")
    chunks = chunk_repository(temp_repo, save=False)
    assert len(chunks) > 0, "Should have chunked at least one code block"
    print(f"✓ Chunked {len(chunks)} code blocks")
    
    # Step 2: Generate REAL embeddings using OpenAI
    print("\n[Step 2/5] Generating real OpenAI embeddings...")
    embedding_service = EmbeddingService()
    
    # Take first 3 chunks to save API costs
    chunks_to_embed = chunks[:3]
    
    # Call async method directly since we're in async context
    embedded_chunks = await embedding_service._generate_embeddings_async(
        chunks_to_embed,
        batch_size=10,
        max_concurrent=2
    )
    
    assert len(embedded_chunks) == len(chunks_to_embed)
    assert all('embedding' in ec for ec in embedded_chunks), "All chunks should have embeddings"
    assert all(len(ec['embedding']) == 3072 for ec in embedded_chunks), "OpenAI embeddings should be 3072-dim"
    print(f"✓ Generated {len(embedded_chunks)} real embeddings (3072 dimensions)")
    
    # Step 3: Store in ChromaDB
    print("\n[Step 3/5] Storing embeddings in ChromaDB...")
    store = ChromaVectorStore(db_path=chromadb_dir)
    collection_name = "e2e_test_real"
    
    result = store.store_embeddings(
        embedded_chunks=embedded_chunks,
        collection_name=collection_name
    )
    
    assert result['stored_count'] == len(embedded_chunks)
    print(f"✓ Stored {result['stored_count']} embeddings in ChromaDB")
    
    # Step 4: Perform semantic search with REAL query
    print("\n[Step 4/5] Testing semantic search...")
    search_query = "function that calculates something"
    search_results = await semantic_search(
        collection_name=collection_name,
        query=search_query,
        n_results=2
    )
    
    assert len(search_results) > 0, "Semantic search should return results"
    assert all('content' in r for r in search_results), "Results should have content"
    print(f"✓ Semantic search returned {len(search_results)} results")
    
    # Step 5: Perform symbol search
    print("\n[Step 5/5] Testing symbol search...")
    # Get a symbol from one of the chunks
    first_chunk_content = embedded_chunks[0]['content']
    
    # Try to find a function definition
    symbol_to_search = None
    for line in first_chunk_content.split('\n'):
        if 'def ' in line:
            # Extract function name
            symbol_to_search = line.split('def ')[1].split('(')[0].strip()
            break
    
    if symbol_to_search:
        symbol_results = await symbol_search(
            collection_name=collection_name,
            symbol_name=symbol_to_search
        )
        assert len(symbol_results) > 0, f"Should find symbol '{symbol_to_search}'"
        print(f"✓ Symbol search found '{symbol_to_search}'")
    else:
        print("⊘ No function definition found to test symbol search")
    
    print("\n" + "="*60)
    print("✅ COMPLETE E2E PIPELINE TEST PASSED!")
    print("="*60)


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
