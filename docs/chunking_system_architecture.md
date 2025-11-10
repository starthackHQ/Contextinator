# Chunking System Architecture

## Overview

The Contextinator chunking system is a sophisticated code analysis pipeline that transforms source code repositories into semantically-rich, searchable chunks optimized for vector embeddings and AI-powered code search. This document provides a comprehensive technical explanation of how the chunking system works, the design decisions behind it, and the structure of the final output.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [The Chunking Pipeline](#the-chunking-pipeline)
3. [Module Breakdown](#module-breakdown)
4. [Chunk Structure](#chunk-structure)
5. [Configuration & Settings](#configuration--settings)
6. [CLI Integration](#cli-integration)
7. [Design Rationale](#design-rationale)
8. [Error Handling & Resilience](#error-handling--resilience)

---

## System Architecture

### Core Components

The chunking system is composed of six primary modules located in `src/contextinator/chunking/`:

1. **file_discovery.py** - Discovers and filters source files
2. **ast_parser.py** - Parses files into Abstract Syntax Trees (ASTs)
3. **node_collector.py** - Collects and deduplicates semantic nodes
4. **context_builder.py** - Enriches chunks with contextual metadata
5. **splitter.py** - Splits large chunks based on token limits
6. **chunk_service.py** - Orchestrates the entire pipeline

### Data Flow

```
Repository Path
    ↓
File Discovery (discover_files)
    ↓
List of File Paths
    ↓
AST Parsing (parse_file) ← Tree-sitter
    ↓
Parsed Nodes with Metadata
    ↓
Node Collection (NodeCollector)
    ↓
Deduplicated Chunks with Enriched Content
    ↓
Chunk Splitting (split_chunk)
    ↓
Final Size-Limited Chunks
    ↓
Save to Disk (chunks.json)
```

---

## The Chunking Pipeline

### Phase 1: File Discovery

**Module**: `file_discovery.py`

The `discover_files()` function recursively scans the repository to identify processable source files.

#### Supported Languages

The system supports 24+ programming languages through the `SUPPORTED_EXTENSIONS` mapping in `config/settings.py`:

- **Languages**: Python (`.py`), JavaScript (`.js`), TypeScript (`.ts`, `.tsx`), Java (`.java`), Go (`.go`), Rust (`.rs`), C/C++ (`.c`, `.cpp`), C# (`.cs`), PHP (`.php`), Bash (`.sh`, `.bash`), SQL (`.sql`), Kotlin (`.kt`, `.kts`), YAML (`.yaml`, `.yml`), Markdown (`.md`), Dockerfile, JSON (`.json`), TOML (`.toml`), Swift (`.swift`), Solidity (`.sol`), Lua (`.lua`)

#### Intelligent Filtering

The system uses `DEFAULT_IGNORE_PATTERNS` (100+ patterns) to exclude:

- **Version Control**: `.git`, `.svn`, `.hg`
- **Python Artifacts**: `__pycache__`, `*.pyc`, `.venv`, `venv`, `env`, `.pytest_cache`, `.mypy_cache`, `*.egg-info`, `dist`, `build`
- **JavaScript/Node**: `node_modules`, `bower_components`, `*.min.js`, `*.bundle.js`, `.next`, `.nuxt`, `.cache`, `.npm`, `.yarn`, `package-lock.json`, `yarn.lock`
- **Java**: `target`, `*.class`, `*.jar`, `*.war`, `.gradle`, `.mvn`
- **C/C++**: `*.o`, `*.so`, `*.dll`, `*.exe`, `cmake-build-*`, `CMakeFiles`
- **Rust**: `target`, `Cargo.lock`
- **Go**: `vendor`, `*.test`
- **C#/.NET**: `bin`, `obj`, `.vs`, `packages`
- **PHP**: `vendor`, `composer.lock`
- **General**: `.DS_Store`, `*.log`, `*.tmp`, `.idea`, `.vscode`

#### Path Normalization

The discovery process normalizes all paths:

- Converts Windows backslashes to forward slashes for cross-platform consistency
- Computes repository-relative paths (not absolute paths)
- Uses both glob-style pattern matching and substring matching via `_should_ignore()`

#### Error Resilience

The function implements graceful error handling:

- Catches `PermissionError` and `OSError` when accessing directories
- Logs warnings for inaccessible paths but continues scanning
- Filters directories in-place to prevent traversal into ignored paths
- Tests file accessibility with `file_path.stat()` before adding to results

**Output**: List of `Path` objects for all supported, accessible files

---

### Phase 2: AST Parsing

**Module**: `ast_parser.py`

This is where semantic intelligence is applied. The `parse_file()` function transforms source code into structured representations.

#### Tree-sitter Integration

The system uses Tree-sitter parsers installed as Python modules:

```python
LANGUAGE_MODULES = {
    'python': tree_sitter_python,
    'javascript': tree_sitter_javascript,
    'typescript': tree_sitter_typescript,
    'tsx': tree_sitter_typescript,  # TSX uses TypeScript module
    'java': tree_sitter_java,
    # ... and 20+ more languages
}
```

**Parser Creation**:

- The `get_parser()` function creates language-specific parsers
- Parsers are cached in `_parser_cache` dictionary (O(languages_used) memory)
- Special handling for TypeScript/TSX: calls `language_typescript()` or `language_tsx()`
- Other languages: calls generic `language()` method

#### Semantic Node Extraction

The `extract_nodes()` function uses language-specific node types defined in `NODE_TYPES`:

**Python**:

- `function_definition`, `class_definition`, `decorated_definition`

**JavaScript/TypeScript**:

- `function_declaration`, `function_expression`, `arrow_function`, `class_declaration`, `method_definition`, `interface_declaration`

**Java**:

- `class_declaration`, `method_declaration`, `constructor_declaration`, `interface_declaration`

**Rust**:

- `function_item`, `impl_item`, `struct_item`, `enum_item`, `trait_item`

**Markdown**:

- `section`, `heading`, `code_block`

**YAML/JSON**:

- `block_mapping`, `block_sequence`, `object`, `array`

#### Node Name Extraction

The `get_node_name()` function implements sophisticated naming logic:

1. **Markdown sections**: Extracts heading text, strips `#` symbols, limits to 50 characters
2. **Arrow functions**: Looks for parent `variable_declarator` to find assigned name, falls back to `arrow_fn_line_X`
3. **JSON/YAML objects**: Searches parent `pair` nodes for keys, uses `object_line_X` as fallback
4. **Standard nodes**: Searches for `identifier`, `name`, `property_identifier`, `type_identifier`, `field_identifier` child nodes
5. **Anonymous nodes**: Generates descriptive names like `anonymous_function_definition_line_42`

#### Fallback Mechanism

When Tree-sitter is unavailable or parsing fails, `_fallback_parse()` is used:

**Fallback Behavior**:

- Creates a single file-level chunk containing the entire file
- Sets `tree_info.has_ast: false` to indicate fallback mode
- Preserves `file_path`, `language`, `content` metadata
- Adds `fallback_reason` explaining why (e.g., "tree-sitter not available or language modules missing")

**Why Fallback?**
The system prioritizes availability over perfection. Even without AST parsing, the system remains functional and can process files as complete units.

#### AST Visualization

When `save_ast=True`, the `_save_ast_safely()` function saves debugging data:

- Calls `save_ast_visualization()` from `ast_visualizer.py`
- Saves to `chunks_dir/ast_trees/` directory
- Includes tree structure, node types, and metadata
- Wrapped in try/except to prevent failures from interrupting chunking

#### Computed Metadata

Each parsed file includes:

```python
{
    'file_path': 'src/auth/login.py',  # Repo-relative with forward slashes
    'language': 'python',
    'content': '<full file content>',
    'nodes': [<extracted nodes>],
    'tree_info': {
        'has_ast': True,
        'root_node_type': 'module',
        'total_nodes': 1247,
        'tree_depth': 18
    }
}
```

**Output**: Dictionary with parsed nodes and metadata, or `None` if file unsupported

---

### Phase 3: Node Collection & Deduplication

**Module**: `node_collector.py`

The `NodeCollector` class manages chunk creation with built-in deduplication.

#### Deduplication Strategy

**Content Hashing**:

- Computes SHA256 hash of code content via `hash_content()` from `utils/hash_utils.py`
- Tracks seen hashes in `self.seen_hashes` set for O(1) lookup
- First occurrence wins: subsequent identical code blocks are not stored

**Duplicate Tracking**:

```python
self.duplicate_locations = {
    'hash_abc123': [
        'src/auth.py:10-25',
        'src/admin_auth.py:45-60',
        'src/utils/helpers.py:102-117'
    ]
}
```

This provides visibility into code duplication patterns without creating redundant chunks.

#### Context Enrichment

The `collect_nodes()` method creates two versions of content for each chunk:

**1. Original Content** (`content`):

- Raw code extracted from AST node
- Used for display and reconstruction

**2. Enriched Content** (`enriched_content`):

- Created by `build_enriched_content()` from `context_builder.py`
- Combines metadata with code for better semantic search

**Enriched Content Structure**:

```
File: src/contextinator/utils/logger.py
Language: python
Type: function_definition
Symbol: configure_logging
Lines: 15-32

def configure_logging(level=logging.INFO):
    """Configure logging for the application."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

#### Chunk Metadata

Each chunk created by the collector includes:

```python
{
    'content': '<raw code>',
    'enriched_content': '<metadata + code>',
    'file_path': 'src/auth/login.py',
    'language': 'python',
    'hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    'node_type': 'function_definition',
    'node_name': 'authenticate_user',
    'start_line': 45,
    'end_line': 62,
    'start_byte': 1203,
    'end_byte': 1687,
    'locations': ['src/auth/login.py:45-62']
}
```

#### Statistics Tracking

The `get_stats()` method returns:

```python
{
    'total_chunks': 342,          # Chunks added to self.chunks
    'unique_hashes': 342,         # Size of self.seen_hashes set
    'duplicates_found': 23,       # Entries in self.duplicate_locations
    'duplicate_locations': {...}  # Map of hash to locations
}
```

**Output**: List of unique, metadata-enriched chunks

---

### Phase 4: Token-Based Splitting

**Module**: `splitter.py`

The `split_chunk()` function handles chunks that exceed token limits.

#### Configuration

From `config/settings.py`:

- **MAX_TOKENS**: 512 tokens per chunk (configurable)
- **CHUNK_OVERLAP**: 50 tokens overlap between consecutive splits

#### Splitting Algorithm

```python
1. Split content into lines using splitlines()
2. Initialize current_split = [] and current_tokens = 0
3. For each line:
   a. Count tokens in line using count_tokens()
   b. If current_tokens + line_tokens > MAX_TOKENS and current_split not empty:
      - Create split from current_split
      - Get overlap lines from end of current_split (_get_overlap_lines)
      - Reset current_split with overlap lines
      - Reset current_tokens to sum of overlap tokens
   c. Append line to current_split
   d. Add line_tokens to current_tokens
4. Create final split from remaining lines
```

**Why Line-Based?**

- Preserves code structure and readability
- Avoids breaking syntax mid-statement
- Maintains logical flow of the code

#### Overlap Mechanism

The `_get_overlap_lines()` function:

1. Works backwards from end of current split
2. Accumulates lines until reaching `overlap_tokens` limit
3. Returns lines in correct order (not reversed)

**Purpose of Overlap**:

- Provides context continuity between adjacent chunks
- Improves embedding quality by capturing transitions
- Ensures queries near split boundaries find relevant results

#### Split Metadata

The `_create_split_chunk()` function adds:

```python
{
    # ... all original metadata preserved
    'content': '<split portion of code>',
    'enriched_content': '<rebuilt with split content>',
    'is_split': True,
    'split_index': 0,              # 0 for first, 1 for second, etc.
    'original_hash': '<hash of original full chunk>',
    'token_count': 487             # Actual tokens in this split
}
```

**Important**: Enriched content is rebuilt for each split by calling `build_enriched_content()` to ensure embeddings have correct context.

#### Edge Cases

- **Empty content**: Returns original chunk unchanged
- **Content fits**: If `total_tokens <= max_tokens`, returns `[chunk]` (no splitting)
- **No splits created**: Returns `[chunk]` as fallback
- **Single line exceeds limit**: Line still gets added (prevents infinite loop)

**Output**: List of split chunks or original chunk if under limit

---

### Phase 5: Orchestration & Statistics

**Module**: `chunk_service.py`

The `chunk_repository()` function orchestrates the entire pipeline.

#### Processing Flow

```python
1. Validate repo_path exists and is directory
2. discover_files(repo_path) → files list
3. Initialize NodeCollector() for deduplication across files
4. Initialize ProgressTracker for user feedback
5. For each file:
   a. parse_file(file_path, save_ast, chunks_dir, repo_path)
   b. collector.collect_nodes(parsed) → unique chunks from file
   c. For each chunk:
      - split_chunk(chunk, max_tokens) → size-limited chunks
      - Append to all_chunks list
   d. Handle errors: log warning, track in failed_files
   e. Update progress tracker
6. Get statistics from collector
7. Optionally save_chunks() to disk
8. Optionally save_ast_overview() for visualization
```

#### Error Handling Philosophy

The system implements **"continue on failure"** pattern throughout:

**File Discovery Errors**:

- Wraps `discover_files()` in try/except
- Raises `FileSystemError` only for critical failures
- Logs permission errors but continues

**Per-File Processing**:

- Each file wrapped in try/except block
- Errors logged as warnings with `logger.warning()`
- Failed file added to `failed_files` list
- Processing continues with next file

**Chunk Splitting Errors**:

- Split failures caught per-chunk
- Original chunk added if splitting fails
- Logs warning but doesn't stop pipeline

**Saving Errors**:

- `save_chunks()` wrapped in try/except
- Returns chunks even if saving fails
- Only logs error, doesn't re-raise

**Why This Approach?**
Large codebases contain edge cases, encoding issues, and unexpected file formats. Partial results are more valuable than complete failure. The system prioritizes availability and completeness over perfection.

#### Statistics Reporting

After processing, the system logs:

```
📊 Chunking Statistics:
  Files processed: 145/150           # 5 files failed
  Unique chunks (before splitting): 342
  Total chunks (after splitting): 389
  Duplicates found: 23               # Deduplication savings
  Chunks split due to size: 47       # Additional chunks created
```

**Calculation**:

- `split_count = len(all_chunks) - stats['unique_hashes']`
- Only shown if `split_count > 0`

#### Saving to Disk

The `save_chunks()` function creates structured JSON:

**File Location**: `.contextinator/chunks/<sanitized_repo_name>/chunks.json`

**Structure**:

```json
{
  "chunks": [
    { /* chunk object 1 */ },
    { /* chunk object 2 */ },
    ...
  ],
  "statistics": {
    "total_chunks": 389,
    "unique_hashes": 342,
    "duplicates_found": 23,
    "duplicate_locations": {
      "hash_123": ["file1.py:10-20", "file2.py:45-55"]
    }
  },
  "repository": "my-repo",
  "version": "1.0",
  "total_chunks": 389
}
```

**Backward Compatibility**: The `load_chunks()` function handles both old (simple array) and new (structured object) formats.

**Output**: List of all chunks (deduplicated and split)

---

## Module Breakdown

### file_discovery.py

**Purpose**: Locate processable source files while respecting ignore patterns

**Key Functions**:

- `discover_files(repo_path, ignore_patterns)` - Main entry point
- `_should_ignore(path, patterns)` - Pattern matching logic

**Implementation Details**:

- Uses `os.walk()` for recursive traversal
- Modifies `dirs` list in-place to prevent traversal into ignored directories
- Normalizes path separators to `/` for cross-platform compatibility
- Uses `fnmatch` for glob patterns and substring matching
- Checks both full path and individual path components

**Error Handling**:

- Catches `PermissionError` and `OSError` per directory
- Logs permission errors but continues
- Raises `ValidationError` for invalid repo_path
- Raises `FileSystemError` for critical scanning errors

---

### ast_parser.py

**Purpose**: Parse source files into semantic AST nodes

**Key Functions**:

- `parse_file(file_path, save_ast, chunks_dir, repo_path)` - Parse single file
- `get_parser(language)` - Get cached tree-sitter parser
- `extract_nodes(root_node, content, language)` - Extract semantic nodes from AST
- `get_node_name(node, content_bytes)` - Extract meaningful node names
- `_fallback_parse()` - File-level chunking fallback
- `_count_nodes(node)` - Count total AST nodes recursively
- `_get_tree_depth(node)` - Calculate maximum tree depth

**Tree-sitter Module Loading**:

```python
try:
    from tree_sitter import Language, Parser
    import tree_sitter_python
    import tree_sitter_javascript
    # ... 20+ more language modules
    TREE_SITTER_AVAILABLE = True
except ImportError as e:
    TREE_SITTER_AVAILABLE = False
    logger.warning(f"Tree-sitter import failed: {e}")
```

**Parser Caching**:

- Global `_parser_cache` dictionary prevents recreating parsers
- Cache key is language string
- Parsers created lazily on first use

**Node Type Filtering**:

- Traverses AST recursively
- Checks `node.type` against `NODE_TYPES[language]`
- Extracts only matching nodes (functions, classes, etc.)
- Continues traversing children even when parent matches

**Path Handling**:

- Computes repo-relative paths using `file_path.relative_to(repo_path)`
- Converts to POSIX format with `.as_posix()` for consistency
- Falls back to absolute path if file outside repo

---

### node_collector.py

**Purpose**: Collect nodes from parsed files with deduplication

**Key Classes**:

- `NodeCollector` - Stateful collector with deduplication

**NodeCollector Attributes**:

- `seen_hashes: Set[str]` - Tracks unique content hashes
- `chunks: List[Dict]` - Collected unique chunks
- `duplicate_locations: Dict[str, List[str]]` - Maps hash to duplicate locations

**collect_nodes() Logic**:

```python
1. Validate parsed_file is dict with 'nodes' key
2. For each node in parsed_file['nodes']:
   a. Extract content and compute hash
   b. Build chunk metadata (file_path, language, node info)
   c. Call build_enriched_content() to create enriched version
   d. Create chunk with both content versions
   e. If hash seen: track location in duplicate_locations
   f. If hash new: add to seen_hashes, chunks, and collected
3. Return collected (unique chunks from this file)
```

**Metadata Extraction**:

- `file_path` from parsed_file
- `language` from parsed_file
- `node_type`, `node_name`, `start_line`, `end_line`, `start_byte`, `end_byte` from node

---

### context_builder.py

**Purpose**: Build contextual information for chunks

**Key Functions**:

- `build_context(chunk)` - Create metadata string
- `build_enriched_content(chunk, content)` - Combine metadata with code

**build_context() Output**:

```
File: src/auth/login.py
Language: python
Type: function_definition
Symbol: authenticate_user
Lines: 45-62
```

**Conditional Fields**:

- Only includes fields present in chunk dictionary
- Checks each field with `if 'field' in chunk and chunk['field']`
- Joins parts with newlines
- Returns empty string if no context parts

**build_enriched_content() Format**:

```
<context from build_context>

<actual code content>
```

Separated by double newline (`\n\n`) for clear delineation.

---

### splitter.py

**Purpose**: Split large chunks based on token limits

**Key Functions**:

- `split_chunk(chunk, max_tokens, overlap)` - Main splitting logic
- `_create_split_chunk(original_chunk, content, split_index)` - Create split with metadata
- `_get_overlap_lines(lines, overlap_tokens)` - Extract overlap from end

**Validation**:

- Raises `TypeError` if chunk not dict
- Raises `ValueError` if max_tokens <= 0, overlap < 0, or overlap >= max_tokens
- Raises `KeyError` if 'content' not in chunk

**Token Counting**:

- Uses `count_tokens()` from `utils/token_counter.py`
- Counts tokens per line and cumulative total
- Checks `current_tokens + line_tokens > max_tokens` before adding line

**Overlap Extraction**:

- Works backwards through lines
- Accumulates until reaching overlap token limit
- Inserts at position 0 to maintain order
- Returns empty list if overlap_tokens <= 0

---

### chunk_service.py

**Purpose**: Orchestrate the complete chunking pipeline

**Key Functions**:

- `chunk_repository()` - Main pipeline orchestration
- `save_chunks()` - Persist chunks to JSON
- `load_chunks()` - Load chunks from JSON

**Validation in chunk_repository()**:

- Checks `repo_path.exists()` - raises `ValidationError` if not
- Checks `repo_path.is_dir()` - raises `ValidationError` if not
- Wraps file discovery in try/except - raises `FileSystemError` on failure

**Progress Tracking**:

- Creates `ProgressTracker(len(files), "Chunking files")`
- Calls `progress.update()` after each file
- Calls `progress.finish()` at end

**Repository Name Handling**:

- Defaults to `repo_path.name` if not provided
- Uses `sanitize_collection_name()` for storage paths

**Storage Path Resolution**:

- Calls `get_storage_path(output_dir, 'chunks', repo_name, custom_chunks_dir)`
- Creates directory with `chunks_dir.mkdir(parents=True, exist_ok=True)`

**AST Visualization**:

- Only saves if `save_ast=True` and `chunks_dir` not None
- Calls `save_ast_overview(chunks_dir)` from `ast_visualizer.py`
- Wrapped in try/except to prevent failures

---

## Chunk Structure

### Basic Chunk Fields

Every chunk contains these core fields:

```python
{
    'content': str,              # Raw code extracted from AST
    'enriched_content': str,     # Context metadata + code for embeddings
    'file_path': str,            # Repo-relative path with forward slashes
    'language': str,             # Programming language identifier
    'hash': str,                 # SHA256 hash of content for deduplication
    'node_type': str,            # AST node type (e.g., 'function_definition')
    'node_name': str | None,     # Extracted or generated node name
    'start_line': int,           # Starting line number (1-indexed)
    'end_line': int,             # Ending line number (inclusive)
    'start_byte': int,           # Starting byte offset in file
    'end_byte': int,             # Ending byte offset in file
    'locations': List[str]       # List of locations (for tracking duplicates)
}
```

### Split Chunk Additional Fields

When a chunk is split due to size, these fields are added:

```python
{
    # ... all basic fields above
    'is_split': bool,            # True if this is a split chunk
    'split_index': int,          # 0 for first split, 1 for second, etc.
    'original_hash': str,        # Hash of the original pre-split chunk
    'token_count': int           # Actual token count in this split
}
```

### Example: Function Chunk

```json
{
  "content": "def authenticate_user(username, password):\n    \"\"\"Authenticate a user with credentials.\"\"\"\n    if not username or not password:\n        return None\n    user = get_user_by_username(username)\n    if user and check_password(password, user.password_hash):\n        return user\n    return None",
  "enriched_content": "File: src/auth/login.py\nLanguage: python\nType: function_definition\nSymbol: authenticate_user\nLines: 45-52\n\ndef authenticate_user(username, password):\n    \"\"\"Authenticate a user with credentials.\"\"\"\n    if not username or not password:\n        return None\n    user = get_user_by_username(username)\n    if user and check_password(password, user.password_hash):\n        return user\n    return None",
  "file_path": "src/auth/login.py",
  "language": "python",
  "hash": "a7f3b8c2d9e1f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f0",
  "node_type": "function_definition",
  "node_name": "authenticate_user",
  "start_line": 45,
  "start_byte": 1203,
  "end_line": 52,
  "end_byte": 1487,
  "locations": ["src/auth/login.py:45-52"]
}
```

### Example: Class Chunk

```json
{
  "content": "class UserManager:\n    \"\"\"Manages user operations.\"\"\"\n    \n    def __init__(self, db_connection):\n        self.db = db_connection\n    \n    def create_user(self, username, email):\n        # implementation\n        pass",
  "enriched_content": "File: src/models/user.py\nLanguage: python\nType: class_definition\nSymbol: UserManager\nLines: 10-19\n\nclass UserManager:\n    \"\"\"Manages user operations.\"\"\"\n    \n    def __init__(self, db_connection):\n        self.db = db_connection\n    \n    def create_user(self, username, email):\n        # implementation\n        pass",
  "file_path": "src/models/user.py",
  "language": "python",
  "hash": "b8g4c9d0e2f5g7h9i1j3k5l7m9n1o3p5q7r9s1t3u5v7w9x1y3z5a7b9c1d3e5f7g9",
  "node_type": "class_definition",
  "node_name": "UserManager",
  "start_line": 10,
  "start_byte": 256,
  "end_line": 19,
  "end_byte": 512,
  "locations": ["src/models/user.py:10-19"]
}
```

### Example: Split Chunk

When a large function exceeds 512 tokens:

**First Split**:

```json
{
  "content": "def process_large_dataset(data):\n    # First 400 lines of implementation\n    results = []\n    for item in data:\n        # complex processing...\n        results.append(processed)\n    # ... continues with overlap",
  "enriched_content": "File: src/processing/batch.py\nLanguage: python\nType: function_definition\nSymbol: process_large_dataset\nLines: 100-299\n\ndef process_large_dataset(data):\n    # First 400 lines...",
  "file_path": "src/processing/batch.py",
  "language": "python",
  "hash": "c9h5d1e3f6g8h0i2j4k6l8m0n2o4p6q8r0s2t4u6v8w0x2y4z6a8b0c2d4e6f8g0",
  "node_type": "function_definition",
  "node_name": "process_large_dataset",
  "start_line": 100,
  "end_line": 299,
  "start_byte": 3000,
  "end_byte": 12000,
  "locations": ["src/processing/batch.py:100-500"],
  "is_split": true,
  "split_index": 0,
  "original_hash": "original_full_function_hash_xyz",
  "token_count": 487
}
```

**Second Split**:

```json
{
  "content": "        # ... overlap from previous split\n        results.append(processed)\n    # Continuation of processing\n    return aggregate_results(results)",
  "enriched_content": "File: src/processing/batch.py\nLanguage: python\nType: function_definition\nSymbol: process_large_dataset\nLines: 280-500\n\n        # ... overlap from previous split...",
  "file_path": "src/processing/batch.py",
  "language": "python",
  "hash": "d0i6e4f7g9h1i3j5k7l9m1n3o5p7q9r1s3t5u7v9w1x3y5z7a9b1c3d5e7f9g1",
  "node_type": "function_definition",
  "node_name": "process_large_dataset",
  "start_line": 280,
  "end_line": 500,
  "start_byte": 10800,
  "end_byte": 18000,
  "locations": ["src/processing/batch.py:100-500"],
  "is_split": true,
  "split_index": 1,
  "original_hash": "original_full_function_hash_xyz",
  "token_count": 412
}
```

### Example: Fallback File-Level Chunk

When AST parsing fails or is unavailable:

```json
{
  "content": "#!/bin/bash\n\n# Complete shell script content\necho 'Hello World'\n# ... entire file",
  "enriched_content": "File: scripts/deploy.sh\nLanguage: bash\nType: file\nSymbol: deploy.sh\nLines: 1-45\n\n#!/bin/bash\n\n# Complete shell script content...",
  "file_path": "scripts/deploy.sh",
  "language": "bash",
  "hash": "e1j7f5g8h0i2j4k6l8m0n2o4p6q8r0s2t4u6v8w0x2y4z6a8b0c2d4e6f8g0h2",
  "node_type": "file",
  "node_name": "deploy.sh",
  "start_line": 1,
  "end_line": 45,
  "start_byte": 0,
  "end_byte": 1523,
  "locations": ["scripts/deploy.sh:1-45"]
}
```

---

## Configuration & Settings

### Module: config/settings.py

#### Chunking Configuration

```python
MAX_TOKENS: int = 512          # Maximum tokens per chunk
CHUNK_OVERLAP: int = 50        # Overlap tokens between splits
```

#### File Discovery Configuration

```python
SUPPORTED_EXTENSIONS: Dict[str, str] = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    # ... 24+ more mappings
    'Dockerfile': 'dockerfile'  # Special case: filename without extension
}

DEFAULT_IGNORE_PATTERNS: List[str] = [
    '.git', '__pycache__', 'node_modules', 'target',
    '*.pyc', '*.min.js', '*.class', # ... 100+ patterns
]
```

#### Storage Configuration

```python
CHUNKS_DIR: str = '.contextinator/chunks'
EMBEDDINGS_DIR: str = '.contextinator/embeddings'
CHROMA_DB_DIR: str = '.contextinator/chromadb'
```

#### Utility Functions

**sanitize_collection_name(repo_name)**:

- Replaces non-alphanumeric characters (except `_` and `-`) with `_`
- Ensures first character is letter or `_`
- Truncates to 63 characters
- Returns `'default_collection'` if result is empty

**get_storage_path(base_dir, storage_type, repo_name, custom_dir)**:

- Validates `storage_type` in `{'chunks', 'embeddings', 'chromadb'}`
- Sanitizes `repo_name` using `sanitize_collection_name()`
- If `custom_dir` provided: returns `base_dir / custom_dir / safe_name`
- Otherwise: returns `base_dir / {CHUNKS_DIR|EMBEDDINGS_DIR|CHROMA_DB_DIR} / safe_name`

**validate_config()**:

- Checks `MAX_TOKENS > 0`
- Checks `CHUNK_OVERLAP >= 0`
- Checks `CHUNK_OVERLAP < MAX_TOKENS`
- Warns if `OPENAI_API_KEY` not set
- Raises `ConfigurationError` for invalid values

---

## CLI Integration

### Module: cli.py

The `chunk_func()` function exposes chunking to the command line.

#### Command Definition

```python
p_chunk = sub.add_parser('chunk', help='Chunks the local Git codebase into semantic units and (optionally) save them')
p_chunk.add_argument('--save', action='store_true', help='Save chunks to .contextinator/chunks/ folder')
p_chunk.add_argument('--save-ast', action='store_true', help='Save AST trees for analysis and debugging')
p_chunk.add_argument('--repo-url', help='GitHub/Git repository URL to clone and chunk')
p_chunk.add_argument('--path', help='Local path to repository (default: current directory)')
p_chunk.add_argument('--output', '-o', help='Output directory for chunks (default: current directory)')
p_chunk.add_argument('--chunks-dir', help='Custom chunks directory (overrides default .contextinator/chunks)')
p_chunk.set_defaults(func=chunk_func)
```

#### chunk_func() Implementation

```python
def chunk_func(args):
    # Extract arguments
    repo_url = getattr(args, 'repo_url', None)

    # Resolve repository path (clone if URL, validate if local)
    repo_path = resolve_repo_path(
        repo_url=repo_url,
        path=getattr(args, 'path', None)
    )

    # Determine repository name
    if repo_url:
        repo_name = extract_repo_name_from_url(repo_url)
    else:
        repo_name = Path(repo_path).name

    # Set output directory
    output_dir = getattr(args, 'output', None) or os.getcwd()

    # Get optional arguments
    custom_chunks_dir = getattr(args, 'chunks_dir', None)
    save_ast = getattr(args, 'save_ast', False)

    # Execute chunking
    chunks = chunk_repository(
        repo_path=repo_path,
        repo_name=repo_name,
        save=args.save,
        output_dir=output_dir,
        save_ast=save_ast,
        custom_chunks_dir=custom_chunks_dir
    )

    # Report results
    logger.info(f"✅ Chunking complete: {len(chunks)} chunks created")

    if args.save:
        chunks_path = get_storage_path(output_dir, 'chunks', repo_name, custom_chunks_dir)
        logger.info(f"Chunks saved in: {chunks_path}/")

    if save_ast:
        logger.info("AST trees saved for analysis")
        chunks_path = get_storage_path(output_dir, 'chunks', repo_name, custom_chunks_dir)
        logger.info(f"Check: {chunks_path}/ast_trees/ for AST files")
```

#### Usage Examples

**Chunk local repository without saving**:

```bash
contextinator chunk --path /path/to/repo
```

**Chunk and save to default location**:

```bash
contextinator chunk --path /path/to/repo --save
```

**Chunk remote repository**:

```bash
contextinator chunk --repo-url https://github.com/user/repo --save
```

**Chunk with custom output directory**:

```bash
contextinator chunk --path /path/to/repo --save --output ./data
```

**Chunk with AST visualization**:

```bash
contextinator chunk --path /path/to/repo --save --save-ast
```

**Chunk with custom chunks directory**:

```bash
contextinator chunk --path /path/to/repo --save --chunks-dir /custom/chunks
```

#### Combined Pipeline

The `chunk-embed-store-embeddings` command runs the full pipeline:

```python
p_pipeline = sub.add_parser('chunk-embed-store-embeddings', help='Run chunk, embed and store-embeddings in a single command')
p_pipeline.add_argument('--save', action='store_true', help='Save intermediate artifacts (chunks + embeddings)')
p_pipeline.add_argument('--repo-url', help='GitHub/Git repository URL to clone and process')
p_pipeline.add_argument('--path', help='Local path to repository (default: current directory)')
p_pipeline.add_argument('--output', '-o', help='Base output directory (default: current directory)')
p_pipeline.add_argument('--chunks-dir', help='Custom chunks directory')
p_pipeline.add_argument('--embeddings-dir', help='Custom embeddings directory')
p_pipeline.add_argument('--chromadb-dir', help='Custom chromadb directory')
p_pipeline.add_argument('--collection-name', help='Custom collection name (default: repository name)')
```

**Pipeline Flow**:

1. Calls `chunk_repository()` with appropriate arguments
2. Passes chunks to `embed_chunks()` for embedding generation
3. Stores embeddings in ChromaDB via `store_repository_embeddings()`
4. Reports statistics for each stage

---

## Design Rationale

### Why AST-Based Chunking?

**Alternative Approaches Considered**:

1. Fixed-size text blocks (e.g., 512-token sliding window)
2. Line-based chunking (e.g., every 50 lines)
3. File-level chunking (entire file as one chunk)

**AST-Based Advantages**:

- **Semantic Coherence**: Each chunk represents a complete, logical unit (function, class, method)
- **Context Preservation**: Implementation details stay together, not split mid-logic
- **Better Embeddings**: Vector representations capture meaningful code patterns
- **Language Awareness**: Different languages have different semantic structures (methods in classes vs. top-level functions)
- **Search Quality**: Queries like "authentication function" match complete implementations

**Implementation Choice**:

- Use Tree-sitter for robust, multi-language AST parsing
- Extract language-specific node types (functions, classes, etc.)
- Fall back to file-level chunking when AST unavailable (availability > perfection)

---

### Why Content Hashing for Deduplication?

**Problem**: Codebases contain duplicated code (boilerplate, copied utilities, generated code)

**Deduplication Benefits**:

- **Storage Efficiency**: Don't store identical code multiple times
- **Embedding Cost**: Don't pay to generate embeddings for duplicates
- **Search Quality**: Avoid returning 50 identical results for common patterns
- **Performance**: Fewer chunks to process and search

**SHA256 Hashing**:

- Cryptographically strong (collision probability negligible)
- Fast to compute (O(content_length))
- Deterministic (same content → same hash)
- Standard library support

**First-Occurrence-Wins**:

- Simplest strategy for deduplication
- Maintains location tracking in `duplicate_locations`
- Provides visibility into duplication patterns

---

### Why Token-Based Splitting with Overlap?

**Problem**: Embedding models have token limits (typically 512-8192 tokens)

**Token Limits by Model**:

- `sentence-transformers/all-MiniLM-L6-v2`: ~512 tokens
- `text-embedding-3-large` (OpenAI): 8191 tokens

**Configuration Choice**: 512 tokens to support smaller models

**Why Overlap?**

1. **Context Continuity**: Adjacent chunks share code, preventing context loss at boundaries
2. **Embedding Quality**: Vector representations capture transitions between sections
3. **Search Completeness**: Queries matching code near boundaries still find relevant chunks

**50-Token Overlap**:

- ~10% of max chunk size
- Balances context preservation with chunk independence
- Minimal redundancy cost

**Line-Based Splitting**:

- Preserves code structure and readability
- Avoids breaking statements mid-syntax
- Maintains logical flow
- Simpler to implement than AST-aware splitting

---

### Why Enriched Content for Embeddings?

**Problem**: Code alone lacks context about WHERE it is and WHAT it represents

**Enriched Content Example**:

```
File: src/auth/login.py
Language: python
Type: function_definition
Symbol: authenticate_user
Lines: 45-62

def authenticate_user(username, password):
    # ... implementation
```

**Benefits**:

1. **Location-Aware Search**: "Find authentication in utils" matches file path
2. **Type-Aware Search**: "Find class definitions" matches node type metadata
3. **Symbol Search**: "authenticate_user function" matches symbol name
4. **Semantic Richness**: Embeddings encode more than just code patterns

**Design Choice**:

- Store both `content` (raw code) and `enriched_content` (metadata + code)
- Embed `enriched_content` for semantic search
- Display `content` for results (users see code, not metadata)
- Separation of concerns: search uses enriched, display uses original

---

### Why "Continue on Failure" Error Handling?

**Philosophy**: Partial results are more valuable than complete failure

**Real-World Scenarios**:

- Large codebases have edge cases (unusual encodings, malformed files)
- Permission issues on some directories
- Unsupported file formats mixed in
- Tree-sitter parsing failures on unusual syntax

**Implementation**:

- Wrap file processing in try/except per file
- Log warnings for failures but continue
- Track failed files for reporting
- Return chunks even if some files failed

**User Experience**:

- System processes as much as possible
- Clear reporting of what failed and why
- Can still use partial results for search
- Option to investigate failures separately

---

### Why Repository Isolation in Storage?

**Storage Structure**:

```
.contextinator/
  chunks/
    repo-name-1/
      chunks.json
      ast_trees/
    repo-name-2/
      chunks.json
  embeddings/
    repo-name-1/
      embeddings.pkl
  chromadb/
    repo-name-1/
      chroma.sqlite3
```

**Benefits**:

1. **Multi-Repository Support**: Process and store multiple repos independently
2. **Namespace Isolation**: No name conflicts between repositories
3. **Selective Updates**: Re-chunk one repo without affecting others
4. **Clear Organization**: Easy to locate data for specific repository
5. **Collection Naming**: ChromaDB collection names match repository names

**Collection Name Sanitization**:

- Ensures ChromaDB naming requirements met (alphanumeric, `_`, `-`)
- Handles special characters in repository names
- Truncates to 63 characters (ChromaDB limit)

---

## Error Handling & Resilience

### Validation Errors

**ValidationError**: Invalid input parameters

**Raised When**:

- `repo_path` doesn't exist or is not a directory
- `repo_name` is empty
- `storage_type` not in valid set
- `save_ast=True` but `chunks_dir=None`
- Configuration values invalid (e.g., `MAX_TOKENS <= 0`)

**Handling**: Immediate failure with clear error message

---

### File System Errors

**FileSystemError**: Problems accessing file system

**Raised When**:

- Cannot read file (permissions, encoding issues)
- Cannot discover files in repository
- Cannot create storage directories

**Handling**:

- Per-file errors: log warning, continue
- Critical errors (e.g., repo path): raise exception
- Directory creation: `mkdir(parents=True, exist_ok=True)`

---

### Parsing Errors

**Sources**:

- Tree-sitter not installed
- Language module missing
- Malformed source code
- Encoding issues

**Handling**:

- Module import failures: set `TREE_SITTER_AVAILABLE = False`, use fallback
- Per-file parse failures: catch exception, use `_fallback_parse()`
- Fallback creates file-level chunk with `has_ast: false`

---

### Chunk Splitting Errors

**Sources**:

- Missing 'content' key in chunk
- Invalid token counts
- Unexpected data types

**Handling**:

- Validation at function entry (raises TypeError, ValueError, KeyError)
- Catch split failures in chunk_service: add original chunk, log warning
- Empty content: return original chunk unchanged

---

### Save/Load Errors

**Sources**:

- Disk full
- Permission denied
- Corrupted JSON
- Missing files

**Handling**:

- Save failures: log error, return chunks anyway (chunks still in memory)
- Load failures: raise FileNotFoundError or JSONDecodeError
- Backward compatibility: handle both old and new JSON formats

---

### Progress Tracking

**ProgressTracker**: Provides user feedback during long operations

**Usage in chunk_repository()**:

```python
progress = ProgressTracker(len(files), "Chunking files")
for file_path in files:
    # ... process file
    progress.update()
progress.finish()
```

**Benefits**:

- Visual feedback for users
- Shows processing status
- Indicates completion
- Helps identify if system is hung vs. processing large files

---

## Performance Characteristics

### Time Complexity

**File Discovery**: O(files × patterns) with early pruning

- `os.walk()` traverses directory tree
- Filters directories in-place to prevent traversal
- Pattern matching per file/directory

**AST Parsing**: O(files × avg_file_size × tree_depth)

- Tree-sitter parsing is generally linear in file size
- Node extraction traverses entire AST

**Deduplication**: O(chunks) with O(1) hash lookups

- SHA256 hashing: O(content_length)
- Set membership check: O(1) average case

**Chunk Splitting**: O(chunks × lines_per_chunk × avg_line_tokens)

- Iterates through lines once per chunk
- Token counting per line

**Total Pipeline**: O(files × avg_file_size)

---

### Space Complexity

**NodeCollector**:

- `seen_hashes`: O(unique_chunks) for deduplication
- `chunks`: O(unique_chunks) for storage
- `duplicate_locations`: O(duplicates × avg_locations)

**Parser Cache**:

- `_parser_cache`: O(languages_used) - typically small (1-10)

**Chunks in Memory**:

- `all_chunks`: O(total_chunks) including splits
- Each chunk stores full content + metadata

**Disk Storage**:

- `chunks.json`: O(total_chunks × avg_chunk_size)
- AST files: O(files) if `save_ast=True`

---

### Optimization Strategies

**Parser Caching**:

- Avoids recreating Tree-sitter parsers
- Reduces initialization overhead

**In-Place Directory Filtering**:

- `dirs[:] = [d for d in dirs if not _should_ignore(d, patterns)]`
- Prevents traversal into ignored directories
- Reduces file discovery time

**Stream Processing**:

- Processes files one at a time
- Doesn't load entire repository into memory
- Memory usage independent of repository size

**Early Returns**:

- Chunk splitting returns immediately if under token limit
- Node extraction skips empty node lists
- Duplicate chunks not added to collector

---

## Summary

The Contextinator chunking system is a production-ready, multi-language code analysis pipeline that:

1. **Discovers** source files using intelligent filtering (100+ ignore patterns)
2. **Parses** code into AST using Tree-sitter (24+ languages)
3. **Extracts** semantic units (functions, classes) with language-specific logic
4. **Deduplicates** using SHA256 content hashing
5. **Enriches** chunks with contextual metadata for better search
6. **Splits** large chunks while preserving context through overlap
7. **Saves** structured JSON with statistics and version information

**Key Design Principles**:

- **Semantic Over Syntactic**: Chunks represent meaningful code units
- **Resilience Over Perfection**: Fallback mechanisms ensure availability
- **Context Preservation**: Enriched content improves search quality
- **Multi-Language Support**: Extensible to any Tree-sitter-supported language
- **Production Quality**: Error handling, progress tracking, configurability

The result is a robust foundation for semantic code search, enabling vector similarity search over intelligently-chunked, context-rich code representations.
