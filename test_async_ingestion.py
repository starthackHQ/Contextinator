"""Test async ingestion with real repositories."""
import asyncio
import time
from src.contextinator import AsyncIngestionService

async def test_single_repo():
    """Test single repo processing."""
    print("\n" + "="*60)
    print("TEST 1: Single Repository (Async)")
    print("="*60)
    
    service = AsyncIngestionService()
    
    repo = {
        "repo_url": "https://github.com/pallets/flask",
        "collection_name": "test_flask_async"
    }
    
    start = time.time()
    result = await service.process_repository_async(
        repo_url=repo["repo_url"],
        collection_name=repo["collection_name"],
        use_async=True,
        max_concurrent=5
    )
    duration = time.time() - start
    
    print(f"\n✅ Result: {result['status']}")
    print(f"⏱️  Duration: {duration:.2f}s")
    print(f"📦 Chunks: {result.get('total_chunks', 0)}")
    print(f"🔮 Embeddings: {result.get('total_embeddings', 0)}")
    
    return result

async def test_batch_repos():
    """Test batch processing (concurrent)."""
    print("\n" + "="*60)
    print("TEST 2: Batch Processing (3 repos concurrently)")
    print("="*60)
    
    service = AsyncIngestionService()
    
    repos = [
        {"repo_url": "https://github.com/psf/requests", "collection_name": "test_requests"},
        {"repo_url": "https://github.com/pallets/click", "collection_name": "test_click"},
        {"repo_url": "https://github.com/pallets/werkzeug", "collection_name": "test_werkzeug"}
    ]
    
    print(f"\n🚀 Processing {len(repos)} repos concurrently...")
    for i, repo in enumerate(repos, 1):
        print(f"   {i}. {repo['repo_url']}")
    
    start = time.time()
    results = await service.process_batch_async(repos, max_concurrent=3)
    duration = time.time() - start
    
    print(f"\n⏱️  Total Duration: {duration:.2f}s")
    print(f"⏱️  Average per repo: {duration/len(repos):.2f}s")
    
    success = sum(1 for r in results if r.get('status') == 'success')
    print(f"\n✅ Success: {success}/{len(repos)}")
    
    for i, result in enumerate(results, 1):
        status = "✅" if result.get('status') == 'success' else "❌"
        chunks = result.get('total_chunks', 0)
        embeddings = result.get('total_embeddings', 0)
        print(f"{status} Repo {i}: {chunks} chunks, {embeddings} embeddings")
    
    return results

async def test_comparison():
    """Compare sync vs async performance."""
    print("\n" + "="*60)
    print("TEST 3: Performance Comparison")
    print("="*60)
    
    service = AsyncIngestionService()
    
    # Small repos for quick test
    repos = [
        {"repo_url": "https://github.com/kennethreitz/setup.py", "collection_name": "test_setup1"},
        {"repo_url": "https://github.com/psf/black", "collection_name": "test_black"}
    ]
    
    # Test async batch
    print("\n🚀 Testing ASYNC batch processing...")
    start_async = time.time()
    results_async = await service.process_batch_async(repos, max_concurrent=2)
    duration_async = time.time() - start_async
    
    print(f"\n⏱️  Async Duration: {duration_async:.2f}s")
    print(f"✅ Async Success: {sum(1 for r in results_async if r.get('status') == 'success')}/{len(repos)}")
    
    return {
        "async_duration": duration_async,
        "async_results": results_async
    }

async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 ASYNC INGESTION SERVICE TESTS")
    print("="*60)
    
    try:
        # Test 1: Single repo
        await test_single_repo()
        
        # Test 2: Batch processing
        await test_batch_repos()
        
        # Test 3: Performance comparison
        await test_comparison()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
