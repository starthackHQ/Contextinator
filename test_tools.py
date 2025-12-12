#!/usr/bin/env python
"""Test all Contextinator search tools"""

from contextinator.tools import (
    semantic_search,
    symbol_search,
    full_text_search,
    regex_search,
    read_file,
    grep_search,
    cat_file
)
from contextinator.tools.repo_structure import analyze_structure

COLLECTION = "test_requests"

print("=" * 80)
print("TESTING CONTEXTINATOR TOOLS")
print("=" * 80)

# Test 1: Semantic Search
print("\n1. SEMANTIC SEARCH - 'HTTP request handling'")
print("-" * 80)
results = semantic_search(COLLECTION, "HTTP request handling", n_results=3)
for i, r in enumerate(results[:3], 1):
    print(f"\n[{i}] {r.get('file_path', 'N/A')} - {r.get('symbol_name', 'N/A')}")
    print(f"    {r.get('content', '')[:100]}...")

# Test 2: Symbol Search
print("\n\n2. SYMBOL SEARCH - 'request'")
print("-" * 80)
results = symbol_search(COLLECTION, "request")
for i, r in enumerate(results[:3], 1):
    print(f"\n[{i}] {r.get('file_path', 'N/A')} - {r.get('symbol_name', 'N/A')}")

# Test 3: Pattern Search
print("\n\n3. PATTERN SEARCH - 'def '")
print("-" * 80)
results = regex_search(COLLECTION, "def ")
for i, r in enumerate(results[:3], 1):
    print(f"\n[{i}] {r.get('file_path', 'N/A')} - {r.get('symbol_name', 'N/A')}")

# Test 4: Full Text Search
print("\n\n4. FULL TEXT SEARCH - 'session'")
print("-" * 80)
results = full_text_search(COLLECTION, "session")
for i, r in enumerate(results[:3], 1):
    print(f"\n[{i}] {r.get('file_path', 'N/A')} - {r.get('symbol_name', 'N/A')}")

# Test 5: Grep Search
print("\n\n5. GREP SEARCH - 'import'")
print("-" * 80)
results = grep_search(COLLECTION, "import", max_chunks=10)
print(f"Found {results['total_matches']} matches in {results['total_files']} files")
for file_result in results['files'][:2]:
    print(f"\n  {file_result['path']}: {len(file_result['matches'])} matches")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED!")
print("=" * 80)
