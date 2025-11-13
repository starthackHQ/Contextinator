# Release Notes Template

## Version [X.Y.Z] - [Date]

### 🚀 New Features
- Added `--chromadb-dir` parameter to all search commands for custom ChromaDB locations
- Enhanced search functionality with flexible database path configuration
- Improved CLI usability for multi-project workflows

### 🔧 Improvements
- Better error handling for ChromaDB connection failures
- Optimized search performance with custom directory support
- Enhanced documentation with new parameter examples

### 🐛 Bug Fixes
- Fixed search commands not finding collections in custom ChromaDB directories
- Resolved path resolution issues in multi-environment setups

### 📚 Documentation
- Updated README with `--chromadb-dir` parameter examples
- Added comprehensive search command documentation
- Included workflow setup instructions

### 🔄 Breaking Changes
- None

### 📦 Installation
```bash
pip install contextinator==X.Y.Z
```

### 🛠️ Usage Examples
```bash
# Use custom ChromaDB directory
contextinator search "query" -c MyRepo --chromadb-dir /path/to/.contextinator/chromadb/

# All search commands now support custom directories
contextinator symbol function_name -c MyRepo --chromadb-dir /custom/path/
```

### 🙏 Contributors
- [@username] - Added custom ChromaDB directory support

---

## Previous Releases

### Version 0.0.96 - 2024-11-14
- Initial release with AST-powered code chunking
- Semantic search with OpenAI embeddings
- ChromaDB vector storage
- Multiple search types: semantic, symbol, pattern, advanced
- TOON format export for LLM optimization
