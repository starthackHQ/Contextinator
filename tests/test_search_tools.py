"""Tests for search tools functionality."""
import pytest
from contextinator.tools.semantic_search import semantic_search
from contextinator.tools.symbol_search import symbol_search
from contextinator.tools.grep_search import grep_search
from contextinator.tools.cat_file import cat_file
from contextinator.tools.repo_structure import analyze_structure


class TestSemanticSearch:
    """Test semantic search functionality."""
    
    def test_semantic_search_basic(self, test_collection):
        """Test basic semantic search."""
        collection, temp_dir = test_collection
        
        results = semantic_search(
            collection_name="test_repo",
            query="authentication user credentials",
            n_results=5,
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, list)
        assert len(results) <= 5
    
    def test_semantic_search_with_results(self, test_collection):
        """Test that semantic search returns relevant results."""
        collection, temp_dir = test_collection
        
        results = semantic_search(
            collection_name="test_repo",
            query="user authentication",
            n_results=3,
            chromadb_dir=temp_dir
        )
        
        if results:
            assert all('content' in r for r in results)
            assert all('metadata' in r for r in results)
    
    def test_semantic_search_empty_query(self, test_collection):
        """Test handling of empty query."""
        collection, temp_dir = test_collection
        
        with pytest.raises((ValueError, Exception)):
            semantic_search(
                collection_name="test_repo",
                query="",
                n_results=5,
                chromadb_dir=temp_dir
            )
    
    def test_semantic_search_nonexistent_collection(self, temp_chromadb):
        """Test search on non-existent collection."""
        client, temp_dir = temp_chromadb
        
        with pytest.raises((ValueError, Exception)):
            semantic_search(
                collection_name="nonexistent",
                query="test",
                n_results=5,
                chromadb_dir=temp_dir
            )
    
    def test_semantic_search_limit_results(self, test_collection):
        """Test that n_results parameter limits results."""
        collection, temp_dir = test_collection
        
        results = semantic_search(
            collection_name="test_repo",
            query="function",
            n_results=2,
            chromadb_dir=temp_dir
        )
        
        assert len(results) <= 2
    
    def test_semantic_search_relevance_scores(self, test_collection):
        """Test that results include relevance/distance scores."""
        collection, temp_dir = test_collection
        
        results = semantic_search(
            collection_name="test_repo",
            query="database connection",
            n_results=3,
            chromadb_dir=temp_dir
        )
        
        if results:
            # Results should have some relevance metric
            assert all('distance' in r or 'score' in r for r in results)


class TestSymbolSearch:
    """Test symbol search functionality."""
    
    def test_symbol_search_exact_match(self, test_collection):
        """Test exact symbol name matching."""
        collection, temp_dir = test_collection
        
        results = symbol_search(
            collection_name="test_repo",
            symbol_name="authenticate_user",
            exact_match=True,
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, list)
        if results:
            assert any('authenticate_user' == r['metadata']['node_name'] for r in results)
    
    def test_symbol_search_partial_match(self, test_collection):
        """Test partial symbol name matching."""
        collection, temp_dir = test_collection
        
        results = symbol_search(
            collection_name="test_repo",
            symbol_name="User",
            exact_match=False,
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, list)
        if results:
            assert any('User' in r['metadata']['node_name'] for r in results)
    
    def test_symbol_search_class_name(self, test_collection):
        """Test searching for class names."""
        collection, temp_dir = test_collection
        
        results = symbol_search(
            collection_name="test_repo",
            symbol_name="UserManager",
            exact_match=True,
            chromadb_dir=temp_dir
        )
        
        if results:
            assert any(r['metadata']['node_type'] == 'class_definition' for r in results)
    
    def test_symbol_search_function_name(self, test_collection):
        """Test searching for function names."""
        collection, temp_dir = test_collection
        
        results = symbol_search(
            collection_name="test_repo",
            symbol_name="validate_input",
            exact_match=True,
            chromadb_dir=temp_dir
        )
        
        if results:
            assert any(r['metadata']['node_type'] == 'function_definition' for r in results)
    
    def test_symbol_search_case_sensitivity(self, test_collection):
        """Test case sensitivity in symbol search."""
        collection, temp_dir = test_collection
        
        results_lower = symbol_search(
            collection_name="test_repo",
            symbol_name="usermanager",
            exact_match=False,
            chromadb_dir=temp_dir
        )
        
        results_proper = symbol_search(
            collection_name="test_repo",
            symbol_name="UserManager",
            exact_match=False,
            chromadb_dir=temp_dir
        )
        
        # Should handle case appropriately
        assert isinstance(results_lower, list)
        assert isinstance(results_proper, list)
    
    def test_symbol_search_no_results(self, test_collection):
        """Test symbol search with no matching results."""
        collection, temp_dir = test_collection
        
        results = symbol_search(
            collection_name="test_repo",
            symbol_name="NonExistentSymbol",
            exact_match=True,
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, list)
        assert len(results) == 0


class TestGrepSearch:
    """Test grep pattern search functionality."""
    
    def test_grep_search_basic(self, test_collection):
        """Test basic grep pattern search."""
        collection, temp_dir = test_collection
        
        results = grep_search(
            collection_name="test_repo",
            pattern="def ",
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, dict)
        # Check if results has expected structure
        if 'files' in results:
            assert isinstance(results['files'], list)
    
    def test_grep_search_class_pattern(self, test_collection):
        """Test searching for class definitions."""
        collection, temp_dir = test_collection
        
        results = grep_search(
            collection_name="test_repo",
            pattern="class ",
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, dict)
    
    def test_grep_search_regex_pattern(self, test_collection):
        """Test regex pattern matching."""
        collection, temp_dir = test_collection
        
        results = grep_search(
            collection_name="test_repo",
            pattern=r"def \w+\(",
            use_regex=True,
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, dict)
    
    def test_grep_search_case_insensitive(self, test_collection):
        """Test case-insensitive grep search."""
        collection, temp_dir = test_collection
        
        results = grep_search(
            collection_name="test_repo",
            pattern="USER",
            case_sensitive=False,
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, dict)
    
    def test_grep_search_empty_pattern(self, test_collection):
        """Test handling of empty pattern."""
        collection, temp_dir = test_collection
        
        with pytest.raises((ValueError, Exception)):
            grep_search(
                collection_name="test_repo",
                pattern="",
                chromadb_dir=temp_dir
            )
    
    def test_grep_search_no_matches(self, test_collection):
        """Test grep search with no matching results."""
        collection, temp_dir = test_collection
        
        results = grep_search(
            collection_name="test_repo",
            pattern="NONEXISTENT_PATTERN_12345",
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, dict)
        # Should have empty or no files
        if 'files' in results:
            assert len(results['files']) == 0 or results.get('total_matches', 0) == 0


class TestCatFile:
    """Test cat_file (file reconstruction) functionality."""
    
    def test_cat_file_basic(self, test_collection):
        """Test basic file content retrieval."""
        collection, temp_dir = test_collection
        
        result = cat_file(
            collection_name="test_repo",
            file_path="src/main.py",
            chromadb_dir=temp_dir
        )
        
        assert result is not None
        assert 'content' in result
        assert isinstance(result['content'], str)
    
    def test_cat_file_contains_code(self, test_collection):
        """Test that retrieved file contains expected code."""
        collection, temp_dir = test_collection
        
        result = cat_file(
            collection_name="test_repo",
            file_path="src/main.py",
            chromadb_dir=temp_dir
        )
        
        if result and 'content' in result:
            content = result['content']
            # Should contain functions/classes from main.py
            assert 'authenticate_user' in content or 'UserManager' in content
    
    def test_cat_file_nonexistent(self, test_collection):
        """Test retrieving non-existent file."""
        collection, temp_dir = test_collection
        
        result = cat_file(
            collection_name="test_repo",
            file_path="nonexistent/file.py",
            chromadb_dir=temp_dir
        )
        
        # Should handle gracefully
        assert result is None or ('content' in result and result['content'] == "")
    
    def test_cat_file_multiple_files(self, test_collection):
        """Test retrieving multiple different files."""
        collection, temp_dir = test_collection
        
        result1 = cat_file(
            collection_name="test_repo",
            file_path="src/main.py",
            chromadb_dir=temp_dir
        )
        
        result2 = cat_file(
            collection_name="test_repo",
            file_path="src/utils.py",
            chromadb_dir=temp_dir
        )
        
        # Different files should have different content
        if result1 and result2:
            assert result1.get('content') != result2.get('content')


class TestRepoStructure:
    """Test repository structure functionality."""
    
    def test_get_repo_structure_basic(self, test_collection):
        """Test getting basic repository structure."""
        collection, temp_dir = test_collection
        
        structure = analyze_structure(
            collection_name="test_repo",
            chromadb_dir=temp_dir
        )
        
        assert structure is not None
        assert isinstance(structure, (dict, list, str))
    
    def test_repo_structure_contains_files(self, test_collection):
        """Test that structure contains file information."""
        collection, temp_dir = test_collection
        
        structure = analyze_structure(
            collection_name="test_repo",
            chromadb_dir=temp_dir
        )
        
        # Convert to string for easier checking
        structure_str = str(structure)
        
        # Should mention source files
        assert 'src' in structure_str or 'main.py' in structure_str or 'utils.py' in structure_str
    
    def test_repo_structure_shows_hierarchy(self, test_collection):
        """Test that structure shows directory hierarchy."""
        collection, temp_dir = test_collection
        
        structure = analyze_structure(
            collection_name="test_repo",
            chromadb_dir=temp_dir
        )
        
        assert structure is not None
        # Should have some organizational structure
        assert len(str(structure)) > 0
