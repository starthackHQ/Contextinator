"""Tests for search tools functionality.

Note: The search tools (grep_search, cat_file, semantic_search, symbol_search)
work on ChromaDB collections containing indexed code, not on raw files directly.
analyze_structure works on the filesystem directly.
"""
import pytest
from pathlib import Path
from contextinator.tools.semantic_search import semantic_search
from contextinator.tools.symbol_search import symbol_search
from contextinator.tools.grep_search import grep_search
from contextinator.tools.cat_file import cat_file
from contextinator.tools.repo_structure import analyze_structure


class TestSemanticSearch:
    """Test semantic search functionality."""
    
    @pytest.mark.asyncio
    async def test_semantic_search_basic(self, test_collection_with_data):
        """Test basic semantic search."""
        store, temp_dir = test_collection_with_data
        
        results = await semantic_search(
            collection_name="test_collection",
            query="calculate numbers",
            n_results=3,
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_semantic_search_with_results(self, test_collection_with_data):
        """Test that semantic search returns relevant results."""
        store, temp_dir = test_collection_with_data
        
        results = await semantic_search(
            collection_name="test_collection",
            query="user authentication",
            n_results=3,
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_semantic_search_empty_query(self, test_collection_with_data):
        """Test handling of empty query."""
        store, temp_dir = test_collection_with_data
        
        with pytest.raises((ValueError, Exception)):
            await semantic_search(
                collection_name="test_collection",
                query="",
                n_results=5,
                chromadb_dir=temp_dir
            )


class TestSymbolSearch:
    """Test symbol search functionality."""
    
    @pytest.mark.asyncio
    async def test_symbol_search_basic(self, test_collection_with_data):
        """Test basic symbol search."""
        store, temp_dir = test_collection_with_data
        
        results = await symbol_search(
            collection_name="test_collection",
            symbol_name="calculate",
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_symbol_search_empty_symbol(self, test_collection_with_data):
        """Test handling of empty symbol."""
        store, temp_dir = test_collection_with_data
        
        with pytest.raises((ValueError, Exception)):
            await symbol_search(
                collection_name="test_collection",
                symbol_name="",
                chromadb_dir=temp_dir
            )


class TestGrepSearch:
    """Test grep search functionality on ChromaDB collections."""
    
    @pytest.mark.asyncio
    async def test_grep_search_basic(self, test_collection_with_data):
        """Test basic grep search on collection."""
        store, temp_dir = test_collection_with_data
        
        results = await grep_search(
            collection_name="test_collection",
            pattern="def",
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, dict)
    
    @pytest.mark.asyncio
    async def test_grep_search_case_insensitive(self, test_collection_with_data):
        """Test case-insensitive grep."""
        store, temp_dir = test_collection_with_data
        
        results = await grep_search(
            collection_name="test_collection",
            pattern="CLASS",
            case_sensitive=False,
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, dict)
    
    @pytest.mark.asyncio
    async def test_grep_search_empty_pattern(self, test_collection_with_data):
        """Test handling of empty pattern."""
        store, temp_dir = test_collection_with_data
        
        with pytest.raises((ValueError, Exception)):
            await grep_search(
                collection_name="test_collection",
                pattern="",
                chromadb_dir=temp_dir
            )
    
    @pytest.mark.asyncio
    async def test_grep_search_regex_pattern(self, test_collection_with_data):
        """Test grep with regex pattern."""
        store, temp_dir = test_collection_with_data
        
        results = await grep_search(
            collection_name="test_collection",
            pattern="def \\w+",
            use_regex=True,
            chromadb_dir=temp_dir
        )
        
        assert isinstance(results, dict)


class TestCatFile:
    """Test cat_file functionality on ChromaDB collections."""
    
    @pytest.mark.asyncio
    async def test_cat_file_basic(self, test_collection_with_data):
        """Test basic file reading from collection."""
        store, temp_dir = test_collection_with_data
        
        content = await cat_file(
            collection_name="test_collection",
            file_path="utils.py",
            chromadb_dir=temp_dir
        )
        
        assert isinstance(content, str)
    
    @pytest.mark.asyncio
    async def test_cat_file_nonexistent(self, test_collection_with_data):
        """Test reading non-existent file from collection."""
        store, temp_dir = test_collection_with_data
        
        with pytest.raises((ValueError, Exception)):
            await cat_file(
                collection_name="test_collection",
                file_path="nonexistent.py",
                chromadb_dir=temp_dir
            )


class TestRepoStructure:
    """Test repository structure analysis (works on filesystem)."""
    
    @pytest.mark.asyncio
    async def test_analyze_structure_basic(self, temp_repo):
        """Test basic repository structure analysis."""
        structure = await analyze_structure(
            repo_path=temp_repo
        )
        
        assert isinstance(structure, str)
        assert len(structure) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_structure_with_max_depth(self, temp_repo):
        """Test structure analysis with depth limit."""
        structure = await analyze_structure(
            repo_path=temp_repo,
            max_depth=2
        )
        
        assert isinstance(structure, str)
    
    @pytest.mark.asyncio
    async def test_analyze_structure_json_format(self, temp_repo):
        """Test structure output in JSON format."""
        structure = await analyze_structure(
            repo_path=temp_repo,
            output_format="json"
        )
        
        assert isinstance(structure, str)
    
    @pytest.mark.asyncio
    async def test_analyze_structure_invalid_path(self):
        """Test structure analysis on invalid path."""
        with pytest.raises((FileNotFoundError, Exception)):
            await analyze_structure(
                repo_path="/nonexistent/path"
            )
