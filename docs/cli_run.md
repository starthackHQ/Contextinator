# Creating Chunks
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contexinator.cli chunk --repo-url https://github.com/iamDyeus/tkreload --save
INFO - Tree-sitter imports successful
INFO - 📥 Cloning https://github.com/iamDyeus/tkreload...
INFO - Repository cloned to C:\Users\Arsh\AppData\Local\Temp\contextinator_mkqo91y_
INFO - Discovering files in C:\Users\Arsh\AppData\Local\Temp\contextinator_mkqo91y_...
INFO - File discovery complete: 17 files found, 0 files ignored
INFO - Found 17 files to process
INFO - Chunking files: 1/17 (5.9%)
INFO - Chunking files: 2/17 (11.8%)
INFO - Chunking files: 3/17 (17.6%)
INFO - Chunking files: 4/17 (23.5%)
INFO - Chunking files: 5/17 (29.4%)
INFO - Chunking files: 6/17 (35.3%)
INFO - Chunking files: 7/17 (41.2%)
INFO - Chunking files: 8/17 (47.1%)
INFO - Chunking files: 9/17 (52.9%)
WARNING - No semantic nodes found in C:\Users\Arsh\AppData\Local\Temp\contextinator_mkqo91y_\tests\__init__.py, using file-level chunking
INFO - Chunking files: 10/17 (58.8%)
INFO - Chunking files: 11/17 (64.7%)
INFO - Chunking files: 12/17 (70.6%)
INFO - Chunking files: 13/17 (76.5%)
INFO - Chunking files: 14/17 (82.4%)
INFO - Chunking files: 15/17 (88.2%)
INFO - Chunking files: 16/17 (94.1%)
WARNING - No semantic nodes found in C:\Users\Arsh\AppData\Local\Temp\contextinator_mkqo91y_\tkreload\__init__.py, using file-level chunking
INFO - Chunking files: 17/17 (100.0%)
INFO - ✅ Chunking files completed: 17/17
INFO -
📊 Chunking Statistics:
INFO -   Files processed: 17/17
INFO -   Total chunks: 93
INFO -   Unique chunks: 89
INFO -   Duplicates found: 0
INFO -
✅ Chunks saved to D:\projects\Contextinator\.contextinator\chunks\tkreload\chunks.json
INFO - ✅ Chunking complete: 93 chunks created
INFO - Chunks saved in: D:\projects\Contextinator\.contextinator\chunks\tkreload/
(.venv) PS D:\projects\Contextinator>      
(.venv) PS D:\projects\Contextinator> python -m src.contexinator.cli embed --repo-url https://github.com/iamDyeus/tkreload --save 
INFO - Tree-sitter imports successful
INFO - 📥 Cloning https://github.com/iamDyeus/tkreload...
INFO - Repository cloned to C:\Users\Arsh\AppData\Local\Temp\contextinator_d_d5dlbj
INFO - Generating embeddings for repository: tkreload
INFO - 📂 Loading chunks from D:\projects\Contextinator\.contextinator\chunks\tkreload\chunks.json
INFO - 📊 Loaded 93 chunks
INFO - 🚀 Starting embedding generation for 93 chunks...
INFO - 📊 Using model: text-embedding-3-large
INFO - 📦 Batch size: 250
INFO - ✅ Processing 92 valid chunks
INFO - Generating embeddings: 1/1 (100.0%)
INFO - ✅ Generating embeddings completed: 1/1
INFO - ✅ Successfully generated embeddings for 92 chunks
INFO - 💾 Embeddings saved to D:\projects\Contextinator\.contextinator\embeddings\tkreload\embeddings.json
INFO - Embedding generation complete: 92 chunks embedded
INFO - Embeddings saved to D:\projects\Contextinator\.contextinator\embeddings\tkreload/
```

# Creating Embeddings
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contexinator.cli embed --repo-url https://github.com/iamDyeus/tkreload --save 
INFO - Tree-sitter imports successful
INFO - 📥 Cloning https://github.com/iamDyeus/tkreload...
INFO - Repository cloned to C:\Users\Arsh\AppData\Local\Temp\contextinator_d_d5dlbj
INFO - Generating embeddings for repository: tkreload
INFO - 📂 Loading chunks from D:\projects\Contextinator\.contextinator\chunks\tkreload\chunks.json
INFO - 📊 Loaded 93 chunks
INFO - 🚀 Starting embedding generation for 93 chunks...
INFO - 📊 Using model: text-embedding-3-large
INFO - 📦 Batch size: 250
INFO - ✅ Processing 92 valid chunks
INFO - Generating embeddings: 1/1 (100.0%)
INFO - ✅ Generating embeddings completed: 1/1
INFO - ✅ Successfully generated embeddings for 92 chunks
INFO - 💾 Embeddings saved to D:\projects\Contextinator\.contextinator\embeddings\tkreload\embeddings.json
INFO - Embedding generation complete: 92 chunks embedded
INFO - Embeddings saved to D:\projects\Contextinator\.contextinator\embeddings\tkreload/
```


# Storing the Embeddings
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contexinator.cli store-embeddings --repo-name tkreload --collection-name Tkreload
INFO - Tree-sitter imports successful
INFO - Storing embeddings for repository: tkreload
INFO - 📂 Loading embeddings from D:\projects\Contextinator\.contextinator\embeddings\tkreload\embeddings.json
INFO - Connecting to ChromaDB server at: http://localhost:8000
INFO - ChromaDB server connection successful
INFO - 🚀 Storing 92 embeddings in ChromaDB...
INFO - 📦 Collection: Tkreload
INFO - 📊 Batch size: 100
INFO - Using existing collection: Tkreload
WARNING - Could not clear existing collection data: At least one of ids, where, or where_document must be provided in delete.
INFO - Storing embeddings: 1/1 (100.0%)
INFO - ✅ Storing embeddings completed: 1/1
INFO - ✅ Successfully stored 92 embeddings
INFO - 📊 Collection now contains 184 items
INFO - Storage complete:
INFO -    📊 Stored: 92 embeddings
INFO -    📚 Collection: Tkreload
INFO -    🗄️  Database: D:\projects\Contextinator\.contextinator\chromadb\tkreload
```
*Note :* here we used the `--repo-name` flag to specify which repository's embeddings to load, and `--collection-name` to name the ChromaDB collection, and also we were using `USE_CHROMA_SERVER=true` and `CHROMA_SERVER_URL=http://localhost:8000` in our `.env` file to connect to the ChromaDB server. the logs here say "🗄️  Database: D:\projects\Contextinator\.contextinator\chromadb\tkreload" ignore that ; )

# Running TOOLs

### 1. Symbol Search
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli symbol "toggle" --collection tkreload
INFO - Tree-sitter imports successful
INFO - 
🔍 Search Results: "Symbol: toggle"
INFO - Collection: tkreload
INFO - Found: 1 result(s)

INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 1/1
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: toggle
INFO - 📍 Lines: 10-14

INFO - def toggle(self):
        """Toggles the auto-reload feature on or off."""
        self.auto_reload = not self.auto_reload
        status = "Enabled" if self.auto_reload else "Disabled"
        self.console.print(f"[bold yellow]Auto-reload is now {status}.[/bold yellow]")

```

### 2. Pattern/Regex Search
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contexinator.cli pattern "\brich\b" --collection Tkreload
INFO - Tree-sitter imports successful
INFO - 
🔍 Search Results: "Pattern: \brich\b"
INFO - Collection: Tkreload
INFO - Found: 3 result(s)

INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 1/3
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: C:\Users\Arsh\AppData\Local\Temp\contextinator_mkqo91y_\pyproject.toml
INFO - 🏷️  Type: table | Symbol: anonymous_table_line_8
INFO - 📍 Lines: 8-28

INFO - [project]
name = "tkreload"
description = "A library that auto reloads your tkinter app whenever file changes are detected."
readme = "README.md"
authors = [{name = "iamDyeus", email = "dyeusyt@gmail.com"}]
license = {text = "Apache License 2.0"}
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Build Tools",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :
... (truncated)
.
.
.
.
```