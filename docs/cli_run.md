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
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli pattern  "\b__init__\b" --collection tkreload

INFO - Tree-sitter imports successful
INFO - 
🔍 Search Results: "Pattern: \b__init__\b"
INFO - Collection: tkreload
INFO - Found: 6 result(s)

INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 1/6
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/app_event_handler.py
INFO - 🏷️  Type: class_definition | Symbol: AppFileEventHandler
INFO - 📍 Lines: 3-42

INFO - class AppFileEventHandler(FileSystemEventHandler):
    """Handles file changes to trigger app reload."""
    def __init__(self, callback, app_file, auto_reload_manager):
        self.callback = callback
        self.app_file = app_file
        self.auto_reload_manager = auto_reload_manager
        self.last_content = None

    def on_modified(self, event):
        """
        Called when a file is modified.

        This method checks if the modified file is the one being monitored
        and i
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 2/6
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/app_event_handler.py
INFO - 🏷️  Type: function_definition | Symbol: __init__
INFO - 📍 Lines: 5-9

INFO - def __init__(self, callback, app_file, auto_reload_manager):
        self.callback = callback
        self.app_file = app_file
        self.auto_reload_manager = auto_reload_manager
        self.last_content = None
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 3/6
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/auto_reload.py
INFO - 🏷️  Type: class_definition | Symbol: AutoReloadManager
INFO - 📍 Lines: 3-18

INFO - class AutoReloadManager:
    """Class to manage the auto-reload feature."""

    def __init__(self, console):
        self.console = console
        self.auto_reload = True  # Initially set to True

    def toggle(self):
        """Toggles the auto-reload feature on or off."""
        self.auto_reload = not self.auto_reload
        status = "Enabled" if self.auto_reload else "Disabled"
        self.console.print(f"[bold yellow]Auto-reload is now {status}.[/bold yellow]")

    def get_status(self
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 4/6
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: __init__
INFO - 📍 Lines: 6-8

INFO - def __init__(self, console):
        self.console = console
        self.auto_reload = True  # Initially set to True
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 5/6
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: class_definition | Symbol: TkreloadApp
INFO - 📍 Lines: 21-124

INFO - class TkreloadApp:
    """Main application class for managing the Tkinter app."""

    def __init__(self, app_file):
        self.console = Console()
        self.auto_reload_manager = AutoReloadManager(console=self.console)
        self.app_file = app_file
        self.process = None
        self.observer = None
        self.reload_count = 0
        self.startup_time=0

    def run_tkinter_app(self):
        """Run the given Tkinter app."""
        show_progress()
        self.process = subproc
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 6/6
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: function_definition | Symbol: __init__
INFO - 📍 Lines: 24-31

INFO - def __init__(self, app_file):
        self.console = Console()
        self.auto_reload_manager = AutoReloadManager(console=self.console)
        self.app_file = app_file
        self.process = None
        self.observer = None
        self.reload_count = 0
        self.startup_time=0
```


### 3.  Semantic Search
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli search "how does autoreload works?" --collection tkreload -n 5
INFO - Tree-sitter imports successful
INFO - 🚀 Starting embedding generation for 1 chunks...
INFO - 📊 Using model: text-embedding-3-large
INFO - 📦 Batch size: 250
INFO - ✅ Processing 1 valid chunks
INFO - Generating embeddings: 1/1 (100.0%)
INFO - ✅ Generating embeddings completed: 1/1
INFO - ✅ Successfully generated embeddings for 1 chunks
INFO - 
🔍 Search Results: "how does autoreload works?"
INFO - Collection: tkreload
INFO - Found: 5 result(s)

INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 1/5 | Similarity: -0.172
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: 🔍 Solution Overview
INFO - 📍 Lines: 33-45

INFO - ## 🔍 Solution Overview

`tkreload` automates reloading for terminal-based Python applications, designed specifically for **Tkinter**. By eliminating the need for manual restarts, it streamlines the development process, saving developers valuable time and enhancing productivity.

**Without tkreload:**
![Without tkreload](https://github.com/iamDyeus/tkreload/blob/main/.assets/without.gif?raw=true)

**With tkreload:**
![With tkreload](https://github.com/iamDyeus/tkreload/blob/main/.assets/with.gif?
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 2/5 | Similarity: -0.212
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: ⏳ Estimated Time Saved with tkreload
INFO - 📍 Lines: 27-33

INFO - ### ⏳ Estimated Time Saved with tkreload

Imagine restarting your terminal application **15 times daily**, with each reload taking **30 seconds**. That’s approximately **7.5 minutes daily** or about **3 hours per month**. `tkreload` helps avoid this productivity drain.   

---


INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 3/5 | Similarity: -0.216
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/auto_reload.py
INFO - 🏷️  Type: class_definition | Symbol: AutoReloadManager
INFO - 📍 Lines: 3-18

INFO - class AutoReloadManager:
    """Class to manage the auto-reload feature."""

    def __init__(self, console):
        self.console = console
        self.auto_reload = True  # Initially set to True

    def toggle(self):
        """Toggles the auto-reload feature on or off."""
        self.auto_reload = not self.auto_reload
        status = "Enabled" if self.auto_reload else "Disabled"
        self.console.print(f"[bold yellow]Auto-reload is now {status}.[/bold yellow]")

    def get_status(self
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 4/5 | Similarity: -0.229
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: get_status
INFO - 📍 Lines: 16-18

INFO - def get_status(self):
        """Returns the current status of auto-reload."""
        return self.auto_reload
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 5/5 | Similarity: -0.243
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: __init__
INFO - 📍 Lines: 6-8

INFO - def __init__(self, console):
        self.console = console
        self.auto_reload = True  # Initially set to True
INFO -
(.venv) PS D:\projects\Contextinator>
```

> [! NOTE]
> semantic search needs improvement FR.
> it gives irrelevant chunks, also need to turn off this "Type" this for this, since its increasing duplication by alot.

### 4. Read Complete File
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli read-file "tkreload/auto_reload.py"  --collection tkreload
INFO - Tree-sitter imports successful
INFO - 
📄 File: tkreload/auto_reload.py
INFO - 📊 Total chunks: 4
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - class AutoReloadManager:
    """Class to manage the auto-reload feature."""

    def __init__(self, console):
        self.console = console
        self.auto_reload = True  # Initially set to True

    def toggle(self):
        """Toggles the auto-reload feature on or off."""
        self.auto_reload = not self.auto_reload
        status = "Enabled" if self.auto_reload else "Disabled"
        self.console.print(f"[bold yellow]Auto-reload is now {status}.[/bold yellow]")

    def get_status(self):
        """Returns the current status of auto-reload."""
        return self.auto_reload
def __init__(self, console):
        self.console = console
        self.auto_reload = True  # Initially set to True
def toggle(self):
        """Toggles the auto-reload feature on or off."""
        self.auto_reload = not self.auto_reload
        status = "Enabled" if self.auto_reload else "Disabled"
        self.console.print(f"[bold yellow]Auto-reload is now {status}.[/bold yellow]")
def get_status(self):
        """Returns the current status of auto-reload."""
        return self.auto_reload
(.venv) PS D:\projects\Contextinator> 
```

> [! NOTE]
> This tools works fine.
> its just that the duplicate chunks (created by breaking same thing into more children(Types) this'll automatically be fixed if we fix the error in the semantic search tool).

### 5. Full Text Search - Advanced Search
```bash

```

