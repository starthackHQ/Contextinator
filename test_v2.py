"""
Test suite for Contextinator v2.0 core functionality
"""

import json
import tempfile
from pathlib import Path


def test_line_mode_basic():
    """Test basic line reading."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("line 1\nline 2\nline 3\nline 4\nline 5\n")
        f.flush()
        temp_path = f.name
    
    try:
        from contextinator import fs_read
        
        # Read all lines
        result = fs_read(temp_path, mode="Line")
        assert result["type"] == "line"
        assert result["total_lines"] == 5
        assert "line 1" in result["content"]
        
        # Read specific range
        result = fs_read(temp_path, mode="Line", start_line=1, end_line=3)
        assert result["lines_returned"] == 2
        assert "line 2" in result["content"]
        assert "line 3" in result["content"]
        
        print("✅ Line mode basic test passed")
    finally:
        Path(temp_path).unlink()


def test_line_mode_negative_indexing():
    """Test negative indexing for line reading."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for i in range(1, 11):
            f.write(f"line {i}\n")
        f.flush()
        temp_path = f.name
    
    try:
        from contextinator import fs_read
        
        # Read last 3 lines
        result = fs_read(temp_path, mode="Line", start_line=-3, end_line=-1)
        assert "line 8" in result["content"]
        assert "line 9" in result["content"]
        assert "line 10" in result["content"]
        
        print("✅ Line mode negative indexing test passed")
    finally:
        Path(temp_path).unlink()


def test_directory_mode():
    """Test directory listing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test structure
        (temp_path / "file1.txt").write_text("content1")
        (temp_path / "file2.txt").write_text("content2")
        (temp_path / "subdir").mkdir()
        (temp_path / "subdir" / "file3.txt").write_text("content3")
        
        from contextinator import fs_read
        
        # Non-recursive
        result = fs_read(str(temp_path), mode="Directory", depth=0)
        assert result["type"] == "directory"
        assert result["total_count"] == 3  # 2 files + 1 dir
        
        # Recursive
        result = fs_read(str(temp_path), mode="Directory", depth=2)
        assert result["total_count"] == 4  # 3 files + 1 dir
        
        print("✅ Directory mode test passed")


def test_search_mode():
    """Test pattern search."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        (temp_path / "file1.py").write_text(
            "def func1():\n"
            "    # TODO: implement\n"
            "    pass\n"
        )
        (temp_path / "file2.py").write_text(
            "def func2():\n"
            "    # TODO: fix bug\n"
            "    return None\n"
        )
        
        from contextinator import fs_read
        
        # Search for TODO
        result = fs_read(str(temp_path), mode="Search", pattern="TODO")
        assert result["type"] == "search"
        assert result["total_matches"] == 2
        
        # Check match details
        match = result["matches"][0]
        assert "file_path" in match
        assert "line_number" in match
        assert "TODO" in match["line_content"]
        assert "context_before" in match
        assert "context_after" in match
        
        print("✅ Search mode test passed")


def test_json_output():
    """Test JSON serialization."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test content\n")
        f.flush()
        temp_path = f.name
    
    try:
        from contextinator import fs_read
        
        result = fs_read(temp_path, mode="Line")
        
        # Should be JSON serializable
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        
        assert parsed["type"] == "line"
        assert "content" in parsed
        
        print("✅ JSON output test passed")
    finally:
        Path(temp_path).unlink()


def run_all_tests():
    """Run all tests."""
    print("🧪 Running Contextinator v2.0 tests...\n")
    
    try:
        test_line_mode_basic()
        test_line_mode_negative_indexing()
        test_directory_mode()
        test_search_mode()
        test_json_output()
        
        print("\n✅ All tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
