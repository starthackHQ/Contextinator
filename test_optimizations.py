#!/usr/bin/env python3
"""Test script to verify performance optimizations."""
import time
from src.chunking import chunk_repository
from src.embedding import embed_chunks


def test_parallel_chunking():
    """Test parallel vs sequential chunking."""
    print("\n" + "="*60)
    print("TEST 1: Parallel Chunking")
    print("="*60)
    
    repo_path = "."  # Current directory
    
    # Test sequential
    print("\n🐌 Testing SEQUENTIAL chunking...")
    start = time.time()
    chunks_seq = chunk_repository(repo_path, parallel=False)
    time_seq = time.time() - start
    print(f"✅ Sequential: {len(chunks_seq)} chunks in {time_seq:.2f}s")
    
    # Test parallel
    print("\n🚀 Testing PARALLEL chunking...")
    start = time.time()
    chunks_par = chunk_repository(repo_path, parallel=True)
    time_par = time.time() - start
    print(f"✅ Parallel: {len(chunks_par)} chunks in {time_par:.2f}s")
    
    # Results
    speedup = time_seq / time_par if time_par > 0 else 0
    print(f"\n📊 SPEEDUP: {speedup:.2f}x faster")
    print(f"   Sequential: {time_seq:.2f}s")
    print(f"   Parallel:   {time_par:.2f}s")
    
    return chunks_par


# def test_async_embedding(chunks):
#     """Test async vs sync embedding."""
#     print("\n" + "="*60)
#     print("TEST 2: Async Embedding")
#     print("="*60)
    
#     # Limit to 100 chunks for testing
#     test_chunks = chunks[:100] if len(chunks) > 100 else chunks
#     print(f"\n📦 Testing with {len(test_chunks)} chunks")
    
#     try:
#         # Test synchronous
#         print("\n🐌 Testing SYNCHRONOUS embedding...")
#         start = time.time()
#         from src.embedding.embedding_service import EmbeddingService
#         service = EmbeddingService()
#         embeddings_sync = service.generate_embeddings(test_chunks, use_async=False)
#         time_sync = time.time() - start
#         print(f"✅ Synchronous: {len(embeddings_sync)} embeddings in {time_sync:.2f}s")
        
#         # Test async
#         print("\n🚀 Testing ASYNC embedding...")
#         start = time.time()
#         embeddings_async = service.generate_embeddings(test_chunks, use_async=True, max_concurrent=10)
#         time_async = time.time() - start
#         print(f"✅ Async: {len(embeddings_async)} embeddings in {time_async:.2f}s")
        
#         # Results
#         speedup = time_sync / time_async if time_async > 0 else 0
#         print(f"\n📊 SPEEDUP: {speedup:.2f}x faster")
#         print(f"   Synchronous: {time_sync:.2f}s")
#         print(f"   Async:       {time_async:.2f}s")
        
#     except Exception as e:
#         print(f"\n⚠️  Embedding test skipped: {e}")
#         print("   (Requires OPENAI_API_KEY in .env)")


def main():
    """Run all tests."""
    print("\n🧪 PERFORMANCE OPTIMIZATION TESTS")
    print("="*60)
    
    # Test 1: Chunking
    chunks = test_parallel_chunking()
    
    # Test 2: Embedding (optional - requires API key)
    # if chunks:
    #     test_async_embedding(chunks)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
