# Creating Chunks
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli chunk --repo-url https://github.com/iamDyeus/tkreload --save
INFO - Tree-sitter imports successful
INFO - 📥 Cloning https://github.com/iamDyeus/tkreload...
INFO - Repository cloned to C:\Users\Arsh\AppData\Local\Temp\contextinator_r2dzatn5
INFO - Discovering files in C:\Users\Arsh\AppData\Local\Temp\contextinator_r2dzatn5...
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
WARNING - No semantic nodes found in C:\Users\Arsh\AppData\Local\Temp\contextinator_r2dzatn5\tests\__init__.py, using file-level chunking
WARNING - Skipping malformed node in tests/__init__.py: 'id'
INFO - Chunking files: 10/17 (58.8%)
INFO - Chunking files: 11/17 (64.7%)
INFO - Chunking files: 12/17 (70.6%)
INFO - Chunking files: 13/17 (76.5%)
INFO - Chunking files: 14/17 (82.4%)
INFO - Chunking files: 15/17 (88.2%)
INFO - Chunking files: 16/17 (94.1%)
WARNING - No semantic nodes found in C:\Users\Arsh\AppData\Local\Temp\contextinator_r2dzatn5\tkreload\__init__.py, using file-level chunking
WARNING - Skipping malformed node in tkreload/__init__.py: 'id'
INFO - Chunking files: 17/17 (100.0%)
INFO - ✅ Chunking files completed: 17/17
INFO - 
📊 Chunking Statistics:
INFO -   Files processed: 17/17
INFO -   Unique chunks (before splitting): 87
INFO -   Total chunks (after splitting): 91
INFO -   Duplicates found: 0
INFO -   Chunks split due to size: 4 additional chunks created
INFO - 
✅ Chunks saved to D:\projects\Contextinator\.contextinator\chunks\tkreload\chunks.json
INFO - ✅ Chunking complete: 91 chunks created
INFO - Chunks saved in: D:\projects\Contextinator\.contextinator\chunks\tkreload/
```

# Creating Embeddings
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli embed --repo-url https://github.com/iamDyeus/tkreload --save 
INFO - Tree-sitter imports successful
INFO - 📥 Cloning https://github.com/iamDyeus/tkreload...
INFO - Repository cloned to C:\Users\Arsh\AppData\Local\Temp\contextinator_wgugsqe9
INFO - Generating embeddings for repository: tkreload
INFO - 📂 Loading chunks from D:\projects\Contextinator\.contextinator\chunks\tkreload\chunks.json
INFO - 📊 Loaded 91 chunks
INFO - 🚀 Starting embedding generation for 91 chunks...
INFO - 📊 Using model: text-embedding-3-large
INFO - 📦 Batch size: 250
INFO - 🔍 Filtered 9 parent chunks (embedding only 82 child chunks)
INFO - ✅ Processing 82 valid chunks
INFO - Generating embeddings: 1/1 (100.0%)
INFO - ✅ Generating embeddings completed: 1/1
INFO - ✅ Successfully generated embeddings for 82 chunks
INFO - 💾 Embeddings saved to D:\projects\Contextinator\.contextinator\embeddings\tkreload\embeddings.json
INFO - Embedding generation complete: 82 chunks embedded
INFO - Embeddings saved to D:\projects\Contextinator\.contextinator\embeddings\tkreload/

```


# Storing the Embeddings
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli store-embeddings --repo-name tkreload --collection-name Tkreload
INFO - Tree-sitter imports successful
INFO - Storing embeddings for repository: tkreload
INFO - 📂 Loading embeddings from D:\projects\Contextinator\.contextinator\embeddings\tkreload\embeddings.json
INFO - Connecting to ChromaDB server at: http://localhost:8000
INFO - ChromaDB server connection successful
INFO - 🚀 Storing 82 embeddings in ChromaDB...
INFO - 📦 Collection: Tkreload
INFO - 📊 Batch size: 100
INFO - Created new collection: Tkreload
INFO - Storing embeddings: 1/1 (100.0%)
INFO - ✅ Storing embeddings completed: 1/1
INFO - ✅ Successfully stored 82 embeddings
INFO - 📊 Collection now contains 82 items
INFO - Storage complete:
INFO -    📊 Stored: 82 embeddings
INFO -    📚 Collection: Tkreload
INFO -    🌐 Saved in ChromaDB server
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

5.1. Find reload-related functions
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli search-advanced --collection tkreload --semantic "reload functionality" --type function_definition --limit 10
INFO - Tree-sitter imports successful
INFO - 🚀 Starting embedding generation for 1 chunks...
INFO - 📊 Using model: text-embedding-3-large
INFO - 📦 Batch size: 250
INFO - ✅ Processing 1 valid chunks
INFO - Generating embeddings: 1/1 (100.0%)
INFO - ✅ Generating embeddings completed: 1/1
INFO - ✅ Successfully generated embeddings for 1 chunks
INFO - 
🔍 Search Results: "Hybrid: reload functionality"
INFO - Collection: tkreload
INFO - Found: 10 result(s)

INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 1/10 | Similarity: -0.442
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: test_toggle_on
INFO - 📍 Lines: 25-29

INFO - def test_toggle_on(self):
        # Test if toggling twice turns auto-reload on again
        self.manager.toggle()  # First toggle to False
        self.manager.toggle()  # Second toggle to True
        self.assertTrue(self.manager.get_status())
INFO - 
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 2/10 | Similarity: -0.444
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_app_event_handler.py
INFO - 🏷️  Type: function_definition | Symbol: test_auto_reload_manager_initial_state
INFO - 📍 Lines: 40-41

INFO - def test_auto_reload_manager_initial_state(self):
        self.assertTrue(self.auto_reload_manager.get_status())
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 3/10 | Similarity: -0.448
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: toggle
INFO - 📍 Lines: 10-14

INFO - def toggle(self):
        """Toggles the auto-reload feature on or off."""
        self.auto_reload = not self.auto_reload
        status = "Enabled" if self.auto_reload else "Disabled"
        self.console.print(f"[bold yellow]Auto-reload is now {status}.[/bold yellow]")
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 4/10 | Similarity: -0.449
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_app_event_handler.py
INFO - 🏷️  Type: function_definition | Symbol: test_auto_reload_manager_toggle 
INFO - 📍 Lines: 33-38

INFO - def test_auto_reload_manager_toggle(self):
        initial_status = self.auto_reload_manager.get_status()
        self.auto_reload_manager.toggle()
        self.assertNotEqual(initial_status, self.auto_reload_manager.get_status())
        self.auto_reload_manager.toggle()
        self.assertEqual(initial_status, self.auto_reload_manager.get_status())
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 5/10 | Similarity: -0.468
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: function_definition | Symbol: toggle_auto_reload
INFO - 📍 Lines: 119-124

INFO - def toggle_auto_reload(self):
        """Toggles auto-reload and updates file monitoring accordingly."""     
        self.auto_reload_manager.toggle()
        if self.auto_reload_manager.get_status():
            self.reload_count = 0
        status = "Enabled" if self.auto_reload_manager.get_status() else "Disabled"
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 6/10 | Similarity: -0.487
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: test_toggle_off
INFO - 📍 Lines: 20-23

INFO - def test_toggle_off(self):
        # Test if toggling changes the auto-reload status to False
        self.manager.toggle()
        self.assertFalse(self.manager.get_status())
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 7/10 | Similarity: -0.490
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: get_status
INFO - 📍 Lines: 16-18

INFO - def get_status(self):
        """Returns the current status of auto-reload."""
        return self.auto_reload
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 8/10 | Similarity: -0.491
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: function_definition | Symbol: monitor_file_changes
INFO - 📍 Lines: 39-53

INFO - def monitor_file_changes(self, on_reload):
        """Monitors app file for changes and triggers reload."""
        if self.observer:
            self.observer.stop()
            self.observer.join()

        event_handler = AppFileEventHandler(
            on_reload, self.app_file, self.auto_reload_manager
        )
        self.observer = Observer()
        self.observer.schedule(
            event_handler, path=os.path.dirname(self.app_file) or ".", recursive=False
        )
        self.obse
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 9/10 | Similarity: -0.501
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
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 10/10 | Similarity: -0.507
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: test_initial_status
INFO - 📍 Lines: 16-18

INFO - def test_initial_status(self):
        # Test if the auto-reload is initially set to True
        self.assertTrue(self.manager.get_status())
```

5.2 Find tkinter GUI code
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli search-advanced --collection tkreload --pattern "tkinter" --language python
INFO - Tree-sitter imports successful
INFO - 
🔍 Search Results: "Advanced: tkinter"
INFO - Collection: tkreload
INFO - Found: 11 result(s)

INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 1/11
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_main.py
INFO - 🏷️  Type: class_definition | Symbol: TestTkreloadApp
INFO - 📍 Lines: 14-71

INFO - class TestTkreloadApp(unittest.TestCase):

    @patch("tkreload.main.subprocess.Popen")
    @patch("tkreload.main.show_progress")
    def test_run_tkinter_app(self, mock_show_progress, mock_popen):
        app = TkreloadApp("example/sample_app.py")
        process = Mock()
        mock_popen.return_value = process

        result = app.run_tkinter_app()
        mock_show_progress.assert_called_once()
        mock_popen.assert_called_once_with([sys.executable, "example/sample_app.py"])
        se
... (truncated)
INFO - 
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 2/11
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_main.py
INFO - 🏷️  Type: decorated_definition | Symbol: test_run_tkinter_app
INFO - 📍 Lines: 16-26

INFO - @patch("tkreload.main.subprocess.Popen")
    @patch("tkreload.main.show_progress")
    def test_run_tkinter_app(self, mock_show_progress, mock_popen):
        app = TkreloadApp("example/sample_app.py")
        process = Mock()
        mock_popen.return_value = process

        result = app.run_tkinter_app()
        mock_show_progress.assert_called_once()
        mock_popen.assert_called_once_with([sys.executable, "example/sample_app.py"])
        self.assertEqual(result, process)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 3/11
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_main.py
INFO - 🏷️  Type: function_definition | Symbol: test_run_tkinter_app
INFO - 📍 Lines: 18-26

INFO - def test_run_tkinter_app(self, mock_show_progress, mock_popen):
        app = TkreloadApp("example/sample_app.py")
        process = Mock()
        mock_popen.return_value = process

        result = app.run_tkinter_app()
        mock_show_progress.assert_called_once()
        mock_popen.assert_called_once_with([sys.executable, "example/sample_app.py"])
        self.assertEqual(result, process)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 4/11
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/help.py
INFO - 🏷️  Type: function_definition | Symbol: show_help
INFO - 📍 Lines: 7-16

INFO - def show_help(auto_reload):
    """Displays help commands with detailed info and rich formatting."""       
    console.print("\n[bold yellow]Tkreload Help:[/bold yellow] [dim](detailed command info)[/dim]\n")
    console.print("[bold cyan]→[/bold cyan] [bold white]Press H[/bold white]     : Display this help section.")
    console.print("[bold cyan]→[/bold cyan] [bold white]Press R[/bold white]     : Restart the Tkinter app.")
    console.print(
        f"[bold cyan]→[/bold cyan] [bold white]Press A[/
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 5/11
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
INFO - Result 6/11
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: function_definition | Symbol: run_tkinter_app
INFO - 📍 Lines: 33-37

INFO - def run_tkinter_app(self):
        """Run the given Tkinter app."""
        show_progress()
        self.process = subprocess.Popen([sys.executable, self.app_file])       
        return self.process
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 7/11
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: function_definition | Symbol: restart_app
INFO - 📍 Lines: 55-65

INFO - def restart_app(self):
        """Restarts the Tkinter app."""
        if self.process:
            self.reload_count += 1
            self.console.log(
                f"[bold yellow]Restarting the Tkinter app... (x{self.reload_count})[/bold yellow]"
            )
            self.process.terminate()
            self.process.wait()
            time.sleep(1)
            self.run_tkinter_app()
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 8/11
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: function_definition | Symbol: start
INFO - 📍 Lines: 67-106

INFO - def start(self):
        """Starts the application, including monitoring and handling commands."""
        start_time = time.time()  # Record the start time
        self.run_tkinter_app()
        self.monitor_file_changes(self.restart_app)
        self.startup_time = (time.time() - start_time) * 1000  # Calculate startup time in milliseconds

        try:
            self.console.print(
                f"\n[bold white]Tkreload ✅[/bold white] [dim](ready in {self.startup_time:.2f} ms)[/dim]\n"

... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 9/11
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: function_definition | Symbol: main
INFO - 📍 Lines: 127-143

INFO - def main():
    parser = argparse.ArgumentParser(
        description="Real-time reload Tkinter app",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("app_file", help="Tkinter app file path")

    args = parser.parse_args()

    app_file = args.app_file

    if not file_exists(app_file):
        Console().print(f"[bold red]Error: File '{app_file}' not found![/bold red]")
        sys.exit(1)

    tkreload_app = TkreloadApp(app_file)
    tkreload_app.sta
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 10/11
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/progress.py
INFO - 🏷️  Type: function_definition | Symbol: show_progress
INFO - 📍 Lines: 9-21

INFO - def show_progress():
    """Display a progress animation when starting the app."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Booting Tkinter app...[/bold green]"),
        BarColumn(bar_width=None),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        transient=True
    ) as progress:
        task = progress.add_task("[green]Starting up...", total=100)
        for _ in range(10):
            progress.update(task, advance=2)
            ti
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 11/11
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/__init__.py
INFO - 🏷️  Type: file | Symbol: __init__.py
INFO - 📍 Lines: 1-12

INFO - """
Tkreload: A tool for automatically reloading Tkinter applications during development.

This package provides functionality to monitor and automatically reload Tkinter
applications, enhancing the development workflow for Tkinter-based projects.   
"""

__all__ = ["TkreloadApp", "AutoReloadManager", "show_help"]

from .main import TkreloadApp
from .auto_reload import AutoReloadManager
from .help import show_help
```

5.3 Find all classes
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli search-advanced --collection tkreload --type class_definition
INFO - Tree-sitter imports successful
INFO - 
🔍 Search Results: "Advanced: metadata filters"
INFO - Collection: tkreload
INFO - Found: 9 result(s)

INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 1/9
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_app_event_handler.py
INFO - 🏷️  Type: class_definition | Symbol: TestAppFileEventHandler
INFO - 📍 Lines: 8-41

INFO - class TestAppFileEventHandler(unittest.TestCase):

    def setUp(self):
        self.callback = Mock()
        self.console = MagicMock(spec=Console)
        self.auto_reload_manager = AutoReloadManager(self.console)
        self.handler = AppFileEventHandler(self.callback, 'example/sample_app.py', self.auto_reload_manager)

    def test_on_modified_app_file_auto_reload_enabled(self):
        # Auto-reload is enabled by default
        event = FileModifiedEvent('example/sample_app.py')
        s
... (truncated)
INFO - 
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 2/9
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_auto_reload.py
INFO - 🏷️  Type: class_definition | Symbol: TestAutoReloadManager
INFO - 📍 Lines: 10-29

INFO - class TestAutoReloadManager(unittest.TestCase):

    def setUp(self):
        self.console = Console()
        self.manager = AutoReloadManager(self.console)

    def test_initial_status(self):
        # Test if the auto-reload is initially set to True
        self.assertTrue(self.manager.get_status())

    def test_toggle_off(self):
        # Test if toggling changes the auto-reload status to False
        self.manager.toggle()
        self.assertFalse(self.manager.get_status())

    def test_t
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 3/9
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_file_utils.py
INFO - 🏷️  Type: class_definition | Symbol: TestFileUtils
INFO - 📍 Lines: 7-27

INFO - class TestFileUtils(unittest.TestCase):

    def test_file_exists(self):
        self.assertTrue(file_exists(__file__))
        self.assertFalse(file_exists('non_existent_file.txt'))

    @patch('os.system')
    def test_clear_terminal_windows(self, mock_system):
        with patch.object(os, 'name', 'nt'):
            clear_terminal()
            mock_system.assert_called_once_with('cls')

    @patch('os.system')
    def test_clear_terminal_unix(self, mock_system):
        with patch.object(os,
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 4/9
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_main.py
INFO - 🏷️  Type: class_definition | Symbol: TestTkreloadApp
INFO - 📍 Lines: 14-71

INFO - class TestTkreloadApp(unittest.TestCase):

    @patch("tkreload.main.subprocess.Popen")
    @patch("tkreload.main.show_progress")
    def test_run_tkinter_app(self, mock_show_progress, mock_popen):
        app = TkreloadApp("example/sample_app.py")
        process = Mock()
        mock_popen.return_value = process

        result = app.run_tkinter_app()
        mock_show_progress.assert_called_once()
        mock_popen.assert_called_once_with([sys.executable, "example/sample_app.py"])
        se
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 5/9
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_main.py
INFO - 🏷️  Type: class_definition | Symbol: TestTkreloadApp
INFO - 📍 Lines: 14-71

INFO -         mock_parser_instance = Mock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_args.side_effect = SystemExit(2)

        with self.assertRaises(SystemExit) as cm:
            main()

        self.assertEqual(cm.exception.code, 2)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 6/9
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
INFO - Result 7/9
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
INFO - Result 8/9
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
INFO - Result 9/9
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: class_definition | Symbol: TkreloadApp
INFO - 📍 Lines: 21-124

INFO -                 "\t[bold cyan]→[/bold cyan] [bold white]Help:[/bold white] Press [bold cyan]H[/bold cyan]\n"
                "\t[bold cyan]→[/bold cyan] [bold white]Restart:[/bold white] Press [bold cyan]R[/bold cyan]\n"
                "\t[bold cyan]→[/bold cyan] [bold white]Exit:[/bold white] Press [bold red]Ctrl + C[/bold red]"
            )


            while True:
                if platform.system() == "Windows":
                    if msvcrt.kbhit():  # Check for keyboard input (Windows    
... (truncated)
```

5.4 # Find file watching logic
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli search-advanced --collection tkreload --semantic "file watcher" --pattern "watch"
INFO - Tree-sitter imports successful
INFO - 🚀 Starting embedding generation for 1 chunks...
INFO - 📊 Using model: text-embedding-3-large
INFO - 📦 Batch size: 250
INFO - ✅ Processing 1 valid chunks
INFO - Generating embeddings: 1/1 (100.0%)
INFO - ✅ Generating embeddings completed: 1/1
INFO - ✅ Successfully generated embeddings for 1 chunks
INFO - 
🔍 Search Results: "Hybrid: file watcher"
INFO - Collection: tkreload
INFO - Found: 50 result(s)

INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 1/50 | Similarity: -0.325
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_main.py
INFO - 🏷️  Type: decorated_definition | Symbol: test_monitor_file_changes
INFO - 📍 Lines: 28-37

INFO - @patch("tkreload.main.Observer")
    @patch("tkreload.main.AppFileEventHandler")
    def test_monitor_file_changes(self, mock_event_handler, mock_observer):
        app = TkreloadApp("example/sample_app.py")
        mock_callback = Mock()

        observer = app.monitor_file_changes(mock_callback)
        mock_event_handler.assert_called_once()
        mock_observer().schedule.assert_called_once()
        mock_observer().start.assert_called_once()
INFO - 
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 2/50 | Similarity: -0.386
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_main.py
INFO - 🏷️  Type: function_definition | Symbol: test_monitor_file_changes
INFO - 📍 Lines: 30-37

INFO - def test_monitor_file_changes(self, mock_event_handler, mock_observer): 
        app = TkreloadApp("example/sample_app.py")
        mock_callback = Mock()

        observer = app.monitor_file_changes(mock_callback)
        mock_event_handler.assert_called_once()
        mock_observer().schedule.assert_called_once()
        mock_observer().start.assert_called_once()
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 3/50 | Similarity: -0.415
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: function_definition | Symbol: monitor_file_changes
INFO - 📍 Lines: 39-53

INFO - def monitor_file_changes(self, on_reload):
        """Monitors app file for changes and triggers reload."""
        if self.observer:
            self.observer.stop()
            self.observer.join()

        event_handler = AppFileEventHandler(
            on_reload, self.app_file, self.auto_reload_manager
        )
        self.observer = Observer()
        self.observer.schedule(
            event_handler, path=os.path.dirname(self.app_file) or ".", recursive=False
        )
        self.obse
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 4/50 | Similarity: -0.449
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
INFO - Result 5/50 | Similarity: -0.509
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_app_event_handler.py
INFO - 🏷️  Type: function_definition | Symbol: test_on_modified_unrelated_file 
INFO - 📍 Lines: 28-31

INFO - def test_on_modified_unrelated_file(self):
        event = FileModifiedEvent('other_file.py')
        self.handler.on_modified(event)
        self.callback.assert_not_called()
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 6/50 | Similarity: -0.525
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
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 7/50 | Similarity: -0.547
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/app_event_handler.py
INFO - 🏷️  Type: function_definition | Symbol: on_modified
INFO - 📍 Lines: 11-26

INFO - def on_modified(self, event):
        """
        Called when a file is modified.

        This method checks if the modified file is the one being monitored     
        and if the auto-reload manager is active. If the content of the file   
        has changed, it triggers the provided callback function.

        Args:
            event: The event object containing information about the file modification.
        """
        if event.src_path.endswith(self.app_file) and self.auto_reload_manager.get_st
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 8/50 | Similarity: -0.550
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: function_definition | Symbol: toggle_auto_reload
INFO - 📍 Lines: 119-124

INFO - def toggle_auto_reload(self):
        """Toggles auto-reload and updates file monitoring accordingly."""     
        self.auto_reload_manager.toggle()
        if self.auto_reload_manager.get_status():
            self.reload_count = 0
        status = "Enabled" if self.auto_reload_manager.get_status() else "Disabled"
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 9/50 | Similarity: -0.561
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: pyproject.toml
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
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 10/50 | Similarity: -0.570
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_app_event_handler.py
INFO - 🏷️  Type: class_definition | Symbol: TestAppFileEventHandler
INFO - 📍 Lines: 8-41

INFO - class TestAppFileEventHandler(unittest.TestCase):

    def setUp(self):
        self.callback = Mock()
        self.console = MagicMock(spec=Console)
        self.auto_reload_manager = AutoReloadManager(self.console)
        self.handler = AppFileEventHandler(self.callback, 'example/sample_app.py', self.auto_reload_manager)

    def test_on_modified_app_file_auto_reload_enabled(self):
        # Auto-reload is enabled by default
        event = FileModifiedEvent('example/sample_app.py')
        s
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 11/50 | Similarity: -0.585
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_app_event_handler.py
INFO - 🏷️  Type: function_definition | Symbol: test_on_modified_app_file_auto_rreload_enabled
INFO - 📍 Lines: 16-20

INFO - def test_on_modified_app_file_auto_reload_enabled(self):
        # Auto-reload is enabled by default
        event = FileModifiedEvent('example/sample_app.py')
        self.handler.on_modified(event)
        self.callback.assert_called_once()
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 12/50 | Similarity: -0.593
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_app_event_handler.py
INFO - 🏷️  Type: function_definition | Symbol: test_on_modified_app_file_auto_rreload_disabled
INFO - 📍 Lines: 22-26

INFO - def test_on_modified_app_file_auto_reload_disabled(self):
        self.auto_reload_manager.toggle()  # Disable auto-reload
        event = FileModifiedEvent('example/sample_app.py')
        self.handler.on_modified(event)
        self.callback.assert_not_called()
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 13/50 | Similarity: -0.608
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_file_utils.py
INFO - 🏷️  Type: class_definition | Symbol: TestFileUtils
INFO - 📍 Lines: 7-27

INFO - class TestFileUtils(unittest.TestCase):

    def test_file_exists(self):
        self.assertTrue(file_exists(__file__))
        self.assertFalse(file_exists('non_existent_file.txt'))

    @patch('os.system')
    def test_clear_terminal_windows(self, mock_system):
        with patch.object(os, 'name', 'nt'):
            clear_terminal()
            mock_system.assert_called_once_with('cls')

    @patch('os.system')
    def test_clear_terminal_unix(self, mock_system):
        with patch.object(os,
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 14/50 | Similarity: -0.612
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: class_definition | Symbol: TkreloadApp
INFO - 📍 Lines: 21-124

INFO -                 "\t[bold cyan]→[/bold cyan] [bold white]Help:[/bold white] Press [bold cyan]H[/bold cyan]\n"
                "\t[bold cyan]→[/bold cyan] [bold white]Restart:[/bold white] Press [bold cyan]R[/bold cyan]\n"
                "\t[bold cyan]→[/bold cyan] [bold white]Exit:[/bold white] Press [bold red]Ctrl + C[/bold red]"
            )


            while True:
                if platform.system() == "Windows":
                    if msvcrt.kbhit():  # Check for keyboard input (Windows    
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 15/50 | Similarity: -0.612
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
INFO - Result 16/50 | Similarity: -0.614
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_file_utils.py
INFO - 🏷️  Type: function_definition | Symbol: test_file_exists
INFO - 📍 Lines: 9-11

INFO - def test_file_exists(self):
        self.assertTrue(file_exists(__file__))
        self.assertFalse(file_exists('non_existent_file.txt'))
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 17/50 | Similarity: -0.624
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: <div align="center">
INFO - 📍 Lines: 1-3

INFO - <div align="center">


INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 18/50 | Similarity: -0.625
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: 🌟 Features
INFO - 📍 Lines: 79-91

INFO - ## 🌟 Features

- **Automatic Reloading:** Automatically restarts Tkinter apps upon file changes.
- **Command-Based Control:**
  - **`H`:** View help commands
  - **`R`:** Restart the application
  - **`A`:** Toggle auto-reload
  - **`Ctrl + C`:** Exit the application
- **Real-Time Feedback:** Uses `rich` for styled console feedback and progress indicators.




INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 19/50 | Similarity: -0.635
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
INFO - Result 20/50 | Similarity: -0.642
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/__init__.py
INFO - 🏷️  Type: file | Symbol: __init__.py
INFO - 📍 Lines: 1-0

INFO -
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 21/50 | Similarity: -0.642
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/file_utils.py
INFO - 🏷️  Type: function_definition | Symbol: file_exists
INFO - 📍 Lines: 10-12

INFO - def file_exists(file_path):
    """Check if a file exists."""
    return os.path.exists(file_path)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 22/50 | Similarity: -0.642
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: example/README.md
INFO - 🏷️  Type: section | Symbol: Demo App
INFO - 📍 Lines: 1-14

INFO - # Demo App

this directory contains sample_app.py, which is a simple tkinter app that demonstrates the use of `tkreload`.

to run the app with `tkreload`, use the following command in your terminal:    

```bash
tkreload sample_app.py
```
<!-- Note -->
> **Note:**
> you'll need to install `tkreload` using `pip install tkreload` first.        
> or install it using `pip install .` from the root directory. (inside `src` folder)

INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 23/50 | Similarity: -0.647
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: 1. Clone the Repository
INFO - 📍 Lines: 53-58

INFO - #### 1. Clone the Repository
```sh
git clone https://github.com/iamDyeus/tkreload.git
cd tkreload
```

INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 24/50 | Similarity: -0.648
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_file_utils.py
INFO - 🏷️  Type: function_definition | Symbol: test_file_exists_with_relative_ppath
INFO - 📍 Lines: 25-27

INFO - def test_file_exists_with_relative_path(self):
        relative_path = os.path.join('tests', 'test_file_utils.py')
        self.assertTrue(file_exists(relative_path))
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 25/50 | Similarity: -0.648
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: ⏳ Estimated Time Saved with tkreload       
INFO - 📍 Lines: 27-33

INFO - ### ⏳ Estimated Time Saved with tkreload

Imagine restarting your terminal application **15 times daily**, with each reload taking **30 seconds**. That’s approximately **7.5 minutes daily** or about **3 hours per month**. `tkreload` helps avoid this productivity drain.

---


INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 26/50 | Similarity: -0.652
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: Acknowledgments
INFO - 📍 Lines: 118-124

INFO - # Acknowledgments
- Inspired by the need for efficient development workflows
- Thanks to all contributors and supporters of this project

## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=iamDyeus/tkreload&type=Date)](https://star-history.com/#iamDyeus/tkreload&Date)

INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 27/50 | Similarity: -0.653
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_app_event_handler.py
INFO - 🏷️  Type: function_definition | Symbol: test_auto_reload_manager_toggle 
INFO - 📍 Lines: 33-38

INFO - def test_auto_reload_manager_toggle(self):
        initial_status = self.auto_reload_manager.get_status()
        self.auto_reload_manager.toggle()
        self.assertNotEqual(initial_status, self.auto_reload_manager.get_status())
        self.auto_reload_manager.toggle()
        self.assertEqual(initial_status, self.auto_reload_manager.get_status())
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 28/50 | Similarity: -0.657
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: 🚀 Problem Statement
INFO - 📍 Lines: 23-33

INFO - ## 🚀 Problem Statement

For developers, frequent manual restarts of terminal applications during development can add up quickly, especially in complex Tkinter projects that require regular updates. `tkreload` provides a solution to this by automating the reload process, resulting in significant time savings.

### ⏳ Estimated Time Saved with tkreload

Imagine restarting your terminal application **15 times daily**, with each reload taking **30 seconds**. That’s approximately **7.5 minutes daily**
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 29/50 | Similarity: -0.660
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: Star History
INFO - 📍 Lines: 122-124

INFO - ## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=iamDyeus/tkreload&type=Date)](https://star-history.com/#iamDyeus/tkreload&Date)

INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 30/50 | Similarity: -0.681
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: function_definition | Symbol: main
INFO - 📍 Lines: 127-143

INFO - def main():
    parser = argparse.ArgumentParser(
        description="Real-time reload Tkinter app",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("app_file", help="Tkinter app file path")

    args = parser.parse_args()

    app_file = args.app_file

    if not file_exists(app_file):
        Console().print(f"[bold red]Error: File '{app_file}' not found![/bold red]")
        sys.exit(1)

    tkreload_app = TkreloadApp(app_file)
    tkreload_app.sta
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 31/50 | Similarity: -0.682
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_app_event_handler.py
INFO - 🏷️  Type: function_definition | Symbol: test_auto_reload_manager_initiall_state
INFO - 📍 Lines: 40-41

INFO - def test_auto_reload_manager_initial_state(self):
        self.assertTrue(self.auto_reload_manager.get_status())
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 32/50 | Similarity: -0.688
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_app_event_handler.py
INFO - 🏷️  Type: function_definition | Symbol: setUp
INFO - 📍 Lines: 10-14

INFO - def setUp(self):
        self.callback = Mock()
        self.console = MagicMock(spec=Console)
        self.auto_reload_manager = AutoReloadManager(self.console)
        self.handler = AppFileEventHandler(self.callback, 'example/sample_app.py', self.auto_reload_manager)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 33/50 | Similarity: -0.690
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
INFO - Result 34/50 | Similarity: -0.690
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_auto_reload.py
INFO - 🏷️  Type: class_definition | Symbol: TestAutoReloadManager
INFO - 📍 Lines: 10-29

INFO - class TestAutoReloadManager(unittest.TestCase):

    def setUp(self):
        self.console = Console()
        self.manager = AutoReloadManager(self.console)

    def test_initial_status(self):
        # Test if the auto-reload is initially set to True
        self.assertTrue(self.manager.get_status())

    def test_toggle_off(self):
        # Test if toggling changes the auto-reload status to False
        self.manager.toggle()
        self.assertFalse(self.manager.get_status())

    def test_t
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 35/50 | Similarity: -0.696
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/__init__.py
INFO - 🏷️  Type: file | Symbol: __init__.py
INFO - 📍 Lines: 1-12

INFO - """
Tkreload: A tool for automatically reloading Tkinter applications during development.

This package provides functionality to monitor and automatically reload Tkinter
applications, enhancing the development workflow for Tkinter-based projects.   
"""

__all__ = ["TkreloadApp", "AutoReloadManager", "show_help"]

from .main import TkreloadApp
from .auto_reload import AutoReloadManager
from .help import show_help

INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 36/50 | Similarity: -0.701
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: ![TkReload-Logo](https://github.com/iamDyeuss/tkrel
INFO - 📍 Lines: 3-69

INFO -
### Installation

#### 1. Clone the Repository
```sh
git clone https://github.com/iamDyeus/tkreload.git
cd tkreload
```
#### 2. Create and activate a virtual environment:
```sh
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install tkreload (in editable mode):
```sh
pip install -e.[test]
```

INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 37/50 | Similarity: -0.702
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tkreload/main.py
INFO - 🏷️  Type: function_definition | Symbol: start
INFO - 📍 Lines: 67-106

INFO - def start(self):
        """Starts the application, including monitoring and handling commands."""
        start_time = time.time()  # Record the start time
        self.run_tkinter_app()
        self.monitor_file_changes(self.restart_app)
        self.startup_time = (time.time() - start_time) * 1000  # Calculate startup time in milliseconds

        try:
            self.console.print(
                f"\n[bold white]Tkreload ✅[/bold white] [dim](ready in {self.startup_time:.2f} ms)[/dim]\n"

... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 38/50 | Similarity: -0.706
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: 2. Create and activate a virtual environmentt:
INFO - 📍 Lines: 58-69

INFO - #### 2. Create and activate a virtual environment:
```sh
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install tkreload (in editable mode):
```sh
pip install -e.[test]
```


INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 39/50 | Similarity: -0.708
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: ![TkReload-Logo](https://github.com/iamDyeuss/tkrel
INFO - 📍 Lines: 3-69

INFO - # ![TkReload-Logo](https://github.com/iamDyeus/tkreload/blob/main/.assets/logo/svg/logo_light.svg?raw=true)

![Static Badge](https://img.shields.io/badge/pip_install-tkreload-purple)      
![Static Badge](https://img.shields.io/badge/Language-Python-red)
![GitHub last commit](https://img.shields.io/github/last-commit/iamDyeus/tkreload)

<h3>
<code>tkreload</code> | Automated Tkinter App Reloading for a Smoother Development Workflow
</h3>

<p align="center">
Effortlessly reload Tkinter-based Python app
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 40/50 | Similarity: -0.709
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_main.py
INFO - 🏷️  Type: class_definition | Symbol: TestTkreloadApp
INFO - 📍 Lines: 14-71

INFO - class TestTkreloadApp(unittest.TestCase):

    @patch("tkreload.main.subprocess.Popen")
    @patch("tkreload.main.show_progress")
    def test_run_tkinter_app(self, mock_show_progress, mock_popen):
        app = TkreloadApp("example/sample_app.py")
        process = Mock()
        mock_popen.return_value = process

        result = app.run_tkinter_app()
        mock_show_progress.assert_called_once()
        mock_popen.assert_called_once_with([sys.executable, "example/sample_app.py"])
        se
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 41/50 | Similarity: -0.715
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: test_toggle_off
INFO - 📍 Lines: 20-23

INFO - def test_toggle_off(self):
        # Test if toggling changes the auto-reload status to False
        self.manager.toggle()
        self.assertFalse(self.manager.get_status())
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 42/50 | Similarity: -0.716
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
INFO - Result 43/50 | Similarity: -0.716
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: pyproject.toml
INFO - 🏷️  Type: table | Symbol: anonymous_table_line_42
INFO - 📍 Lines: 42-46

INFO - [tool.setuptools.packages.find]
include = ["tkreload", "tkreload.*"]
namespaces = false


INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 44/50 | Similarity: -0.718
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: Testing
INFO - 📍 Lines: 91-102

INFO - ## Testing
To verify tkreload functionality, follow these steps:

1.Install Testing Dependencies: Make sure all testing libraries are installed as per the requirements.txt file.

2.Run Tests Using Pytest
```bash
pytest -v
```
This will run the test suite and confirm tkreload is working as expected.      


INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 45/50 | Similarity: -0.726
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: Usage
INFO - 📍 Lines: 69-102

INFO - # Usage

To run the app with `tkreload`, use the following command in your terminal:    

```bash
tkreload your_app.py
```

Now, whenever you save changes to your script, tkreload will automatically reload your application.

## 🌟 Features

- **Automatic Reloading:** Automatically restarts Tkinter apps upon file changes.
- **Command-Based Control:**
  - **`H`:** View help commands
  - **`R`:** Restart the application
  - **`A`:** Toggle auto-reload
  - **`Ctrl + C`:** Exit the application
- **Real-Ti
... (truncated)
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 46/50 | Similarity: -0.726
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: License
INFO - 📍 Lines: 114-118

INFO - # License

Distributed under the Apache-2.0 License. See [`LICENSE`](LICENSE) for more information.


INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 47/50 | Similarity: -0.737
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: README.md
INFO - 🏷️  Type: section | Symbol: Installation
INFO - 📍 Lines: 51-69

INFO - ### Installation

#### 1. Clone the Repository
```sh
git clone https://github.com/iamDyeus/tkreload.git
cd tkreload
```
#### 2. Create and activate a virtual environment:
```sh
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install tkreload (in editable mode):
```sh
pip install -e.[test]
```


INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 48/50 | Similarity: -0.737
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: test_initial_status
INFO - 📍 Lines: 16-18

INFO - def test_initial_status(self):
        # Test if the auto-reload is initially set to True
        self.assertTrue(self.manager.get_status())
INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 49/50 | Similarity: -0.739
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: pyproject.toml
INFO - 🏷️  Type: table | Symbol: anonymous_table_line_39
INFO - 📍 Lines: 39-42

INFO - [project.scripts]
tkreload = "tkreload.main:main"


INFO -
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - Result 50/50 | Similarity: -0.739
INFO - ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO - 📄 File: tests/test_auto_reload.py
INFO - 🏷️  Type: function_definition | Symbol: test_toggle_on
INFO - 📍 Lines: 25-29

INFO - def test_toggle_on(self):
        # Test if toggling twice turns auto-reload on again
        self.manager.toggle()  # First toggle to False
        self.manager.toggle()  # Second toggle to True
        self.assertTrue(self.manager.get_status())
```

5.5 Export comprehensive search
```bash
(.venv) PS D:\projects\Contextinator> python -m src.contextinator.cli search-advanced --collection tkreload --semantic "main application logic" --json tkreload_analysis.json
INFO - Tree-sitter imports successful
INFO - 🚀 Starting embedding generation for 1 chunks...
INFO - 📊 Using model: text-embedding-3-large
INFO - 📦 Batch size: 250
INFO - ✅ Processing 1 valid chunks
INFO - Generating embeddings: 1/1 (100.0%)
INFO - ✅ Generating embeddings completed: 1/1
INFO - ✅ Successfully generated embeddings for 1 chunks
INFO - ✅ Results exported to: tkreload_analysis.json
(.venv) PS D:\projects\Contextinator>
```
> [! WARNING]
> This Fucking
> gave me a 1000 line json as output, probably needs something like a --limit to it.