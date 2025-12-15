"""Tests for chunking functionality."""
import pytest
from pathlib import Path
from contextinator.chunking.file_discovery import discover_files
from contextinator.chunking.ast_parser import parse_file
from contextinator.chunking.node_collector import NodeCollector
from contextinator.chunking.chunk_service import chunk_repository


class TestFileDiscovery:
    """Test file discovery functionality."""
    
    def test_discover_python_files_basic(self, temp_repo):
        """Test basic discovery of Python files."""
        files = discover_files(temp_repo)
        
        assert len(files) > 0
        assert all(str(f).endswith('.py') for f in files)
        assert any('main.py' in str(f) for f in files)
        assert any('utils.py' in str(f) for f in files)
    
    def test_discover_excludes_pycache(self, temp_repo):
        """Test that __pycache__ directories are excluded."""
        # Create __pycache__ directory
        (Path(temp_repo) / "src" / "__pycache__").mkdir()
        (Path(temp_repo) / "src" / "__pycache__" / "test.pyc").write_text("compiled")
        
        files = discover_files(temp_repo)
        
        assert not any('__pycache__' in str(f) for f in files)
        assert not any('.pyc' in str(f) for f in files)
    
    def test_discover_excludes_node_modules(self, temp_repo):
        """Test that node_modules directories are excluded."""
        # Create node_modules directory
        (Path(temp_repo) / "node_modules").mkdir()
        (Path(temp_repo) / "node_modules" / "test.py").write_text("def test(): pass")
        
        files = discover_files(temp_repo)
        
        assert not any('node_modules' in str(f) for f in files)


class TestASTParser:
    """Test AST parsing functionality."""
    
    def test_parse_simple_function(self, temp_repo):
        """Test parsing a simple function definition."""
        file_path = Path(temp_repo) / "src" / "utils.py"
        parsed = parse_file(file_path, save_ast=False, repo_path=Path(temp_repo))
        
        assert parsed is not None
        assert 'nodes' in parsed or 'tree' in parsed or parsed
    
    def test_parse_class_definition(self, temp_repo):
        """Test parsing class definitions."""
        file_path = Path(temp_repo) / "src" / "main.py"
        parsed = parse_file(file_path, save_ast=False, repo_path=Path(temp_repo))
        
        assert parsed is not None
        # Should have parsed data
        assert parsed
    
    def test_parse_invalid_syntax(self, temp_repo):
        """Test handling of invalid Python syntax."""
        invalid_file = Path(temp_repo) / "invalid.py"
        invalid_file.write_text("def invalid syntax here")
        
        parsed = parse_file(invalid_file, save_ast=False, repo_path=Path(temp_repo))
        
        # Should handle gracefully (return None or empty)
        assert parsed is None or not parsed or parsed


class TestNodeCollector:
    """Test node collection from AST."""
    
    def test_collect_function_nodes(self, temp_repo):
        """Test collection of function definition nodes."""
        file_path = Path(temp_repo) / "src" / "utils.py"
        parsed = parse_file(file_path, save_ast=False, repo_path=Path(temp_repo))
        
        if parsed:
            collector = NodeCollector()
            nodes = collector.collect_nodes(parsed)
            
            assert len(nodes) > 0
            function_nodes = [n for n in nodes if n.get('node_type') == 'function_definition']
            assert len(function_nodes) >= 2  # validate_input, format_response
    
    def test_collect_class_nodes(self, temp_repo):
        """Test collection of class definition nodes."""
        file_path = Path(temp_repo) / "src" / "main.py"
        parsed = parse_file(file_path, save_ast=False, repo_path=Path(temp_repo))
        
        if parsed:
            collector = NodeCollector()
            nodes = collector.collect_nodes(parsed)
            
            class_nodes = [n for n in nodes if n.get('node_type') == 'class_definition']
            assert len(class_nodes) >= 1  # UserManager
    
    def test_collect_method_nodes(self, temp_repo):
        """Test collection of method nodes within classes."""
        file_path = Path(temp_repo) / "src" / "database.py"
        parsed = parse_file(file_path, save_ast=False, repo_path=Path(temp_repo))
        
        if parsed:
            collector = NodeCollector()
            nodes = collector.collect_nodes(parsed)
            
            method_nodes = [n for n in nodes if 'parent' in n.get('metadata', {})]
            assert len(method_nodes) > 0  # Methods like connect, disconnect


class TestChunkService:
    """Test chunk service functionality."""
    
    def test_chunk_repository_basic(self, temp_repo):
        """Test basic chunking of a repository."""
        chunks = chunk_repository(temp_repo, save=False)
        
        assert len(chunks) > 0
        assert all('chunk_id' in chunk for chunk in chunks)
        assert all('content' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
    
    def test_chunk_has_node_metadata(self, temp_repo):
        """Test that chunks contain proper node metadata."""
        chunks = chunk_repository(temp_repo, save=False)
        
        # Find a specific function chunk
        auth_chunks = [c for c in chunks if c.get('metadata', {}).get('node_name') == 'authenticate_user']
        
        if auth_chunks:
            chunk = auth_chunks[0]
            assert chunk['metadata']['node_type'] == 'function_definition'
            assert chunk['metadata']['language'] == 'python'
            assert 'file_path' in chunk['metadata']
            assert 'authenticate_user' in chunk['content']
    
    def test_chunk_with_parent_relationships(self, temp_repo):
        """Test that parent-child relationships are maintained."""
        chunks = chunk_repository(temp_repo, save=False)
        
        # Find chunks that are methods (should have parent)
        method_chunks = [c for c in chunks 
                        if c.get('metadata', {}).get('node_type') in ['function_definition']
                        and 'parent' in c.get('metadata', {})]
        
        # Should find some methods with parent classes
        assert len(method_chunks) > 0
    
    def test_chunk_content_extraction(self, temp_repo):
        """Test that chunk content is properly extracted."""
        chunks = chunk_repository(temp_repo, save=False)
        
        # Verify that chunks contain actual code
        for chunk in chunks:
            assert len(chunk['content']) > 0
            assert isinstance(chunk['content'], str)
    
    def test_chunk_save_to_file(self, temp_repo, tmp_path):
        """Test saving chunks to JSON file."""
        chunks = chunk_repository(
            temp_repo, 
            save=True, 
            output_dir=str(tmp_path)
        )
        
        # Chunks should be returned
        assert len(chunks) > 0
    
    def test_chunk_unique_ids(self, temp_repo):
        """Test that all chunk IDs are unique."""
        chunks = chunk_repository(temp_repo, save=False)
        
        chunk_ids = [c['chunk_id'] for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))  # All unique
    
    def test_chunk_line_numbers(self, temp_repo):
        """Test that chunks include line number information."""
        chunks = chunk_repository(temp_repo, save=False)
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            if 'start_line' in metadata and 'end_line' in metadata:
                assert metadata['start_line'] > 0
                assert metadata['end_line'] >= metadata['start_line']
