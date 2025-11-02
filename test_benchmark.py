#!/usr/bin/env python3
"""Test benchmark with 5 repos to verify resource management works."""
import os
import time
import subprocess
from datetime import datetime

# Small test set
TEST_REPOS = [
    "https://github.com/pallets/click",
    "https://github.com/chalk/chalk", 
    "https://github.com/gin-gonic/gin",
    "https://github.com/clap-rs/clap",
    "https://github.com/google/gson"
]

def run_chunk_command(repo_url, index, total):
    """Run chunking with limited workers."""
    print(f"\n[{index}/{total}] {repo_url}")
    
    start_time = time.time()
    
    try:
        env = {"CONTEXTINATOR_MAX_WORKERS": "2"}
        
        result = subprocess.run(
            ["python", "-m", "src.cli", "chunk", "--save", "--repo-url", repo_url],
            capture_output=True,
            text=True,
            timeout=120,
            env={**dict(os.environ), **env}
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {elapsed:.1f}s")
            return {'status': 'success', 'time': elapsed}
        else:
            print(f"❌ {elapsed:.1f}s")
            return {'status': 'failed', 'time': elapsed}
    
    except subprocess.TimeoutExpired:
        print(f"⏱️ TIMEOUT")
        return {'status': 'timeout', 'time': 120}
    
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return {'status': 'error', 'time': 0}

def main():
    print(f"🧪 Testing with {len(TEST_REPOS)} repos")
    
    start_time = time.time()
    results = []
    
    for i, repo in enumerate(TEST_REPOS, 1):
        result = run_chunk_command(repo, i, len(TEST_REPOS))
        results.append(result)
    
    elapsed = time.time() - start_time
    success = sum(1 for r in results if r['status'] == 'success')
    
    print(f"\n📊 Test Results: {success}/{len(TEST_REPOS)} successful in {elapsed:.1f}s")

if __name__ == "__main__":
    main()
