<img src="https://raw.githubusercontent.com/starthackHQ/Contextinator/main/docs/banner.webp" alt="Contextinator" width="100%" />
<br />
<p align="center">
Turn any codebase into searchable knowledge for AI-powered workflows.
</p>

### Key Features

#### Core (Rust-Powered - Zero Dependencies)

- **🚀 Blazing Fast** - Rust-powered filesystem operations for AI agents
- **📖 Smart File Reading** - Read files with line ranges (including negative indexing)
- **📁 Directory Listing** - Recursive and non-recursive directory traversal
- **🔍 Pattern Search** - Fast pattern matching with context lines
- **🔄 Batch Operations** - Process multiple operations in parallel
- **🌐 JSON Output** - Machine-readable output for agent integration
- **💡 Zero Dependencies** - Core functionality requires no external dependencies

#### Optional RAG Features (Install with `pip install contextinator[rag]`)

- **AST-Powered Chunking** - Extract functions, classes, and methods from 23+ programming languages
- **Parent-Child Relationships** - Maintain hierarchical chunk-context for complete understanding
- **Semantic Search** - Find relevant code using natural language queries
- **Multiple Search Modes** - Semantic, symbol-based, pattern matching, and hybrid search
- **TOON Format Export** - Token-efficient output format for LLM prompts (40-60% token savings)
- **Docker-Ready** - ChromaDB server included

### Use Cases

| **AI Agent Filesystem Tools (v2 Core)** | **RAG Applications (Optional)**                          | **Code Intelligence**                      |
| --------------------------------------- | -------------------------------------------------------- | ------------------------------------------ |
| Fast file reading for AI agents         | High-precision code retrieval with embeddings            | Cross-repository code search and discovery |
| Directory traversal and exploration     | Context injection for code explanation and documentation | Duplicate and similar code detection       |
| Pattern matching in codebases           | Semantic code search across repositories                 | Legacy codebase analysis and understanding |
| Batch filesystem operations             | Parent-child relationship tracking for complete context  | MCP-compliant async architecture           |

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Optional: Docker (for RAG features with ChromaDB)
- Optional: OpenAI API key (for RAG embeddings)

### Installation

**Core (Rust-powered tools only):**

```bash
pip install contextinator
```

**With RAG features:**

```bash
pip install contextinator[rag]
```

Verify the installation:

```bash
contextinator --help
```

For detailed setup and configuration, see [`USAGE.md`](https://github.com/starthackHQ/Contextinator/blob/main/USAGE.md)

---

## Quick Start - v2.0 (Rust-Powered)

### 1. Read Files with Line Ranges

```bash
# Read specific line range
contextinator read --path myfile.py --mode Line --start-line 10 --end-line 50

# Read last 10 lines (negative indexing)
contextinator read --path myfile.py --mode Line --start-line -10 --end-line -1

# Read entire file
contextinator read --path myfile.py --mode Line
```

### 2. List Directory Contents

```bash
# Non-recursive listing
contextinator read --path src/ --mode Directory --depth 0

# Recursive listing (depth 2)
contextinator read --path src/ --mode Directory --depth 2

# JSON output for agents
contextinator read --path src/ --mode Directory --format json
```

### 3. Search for Patterns

```bash
# Find TODOs with context
contextinator read --path . --mode Search --pattern "TODO" --context-lines 2

# Find function definitions
contextinator read --path src/ --mode Search --pattern "def " --context-lines 5

# JSON output
contextinator read --path . --mode Search --pattern "FIXME" --format json
```

### 4. Python API

```python
from contextinator import fs_read

# Read file lines
result = fs_read("file.py", mode="Line", start_line=10, end_line=50)

# List directory
result = fs_read("src/", mode="Directory", depth=2)

# Search patterns
result = fs_read(".", mode="Search", pattern="TODO", context_lines=2)
```

---

## Optional: RAG Features

For semantic code search and advanced code intelligence, install RAG extras:

```bash
pip install contextinator[rag]
```

### Index a Repository:

```bash
contextinator --rag chunk --path ./myrepo --save
contextinator --rag embed --path ./myrepo --save
contextinator --rag store-embeddings --path ./myrepo --collection-name MyRepo
```

### Search with Semantic Understanding:

```bash
# Natural language semantic search
contextinator --rag search "authentication logic" --collection MyRepo

# Find specific functions
contextinator --rag symbol authenticate_user --collection MyRepo

# Export results in TOON format for LLM consumption
contextinator --rag search "error handling" --collection MyRepo --toon results.json
```

For comprehensive CLI and RAG documentation, see [`USAGE.md`](https://github.com/starthackHQ/Contextinator/blob/main/USAGE.md)

## Acknowledgements

Built with and inspired by amazing open-source projects:

### Core Technologies

- **[Rust](https://www.rust-lang.org/)** - Systems programming language for blazing-fast performance
- **[PyO3](https://github.com/PyO3/pyo3)** - Rust bindings for Python
- **[tree-sitter](https://github.com/tree-sitter/tree-sitter)** - Incremental parsing system for AST generation (RAG features)
- **[ChromaDB](https://github.com/chroma-core/chroma)** - AI-native embedding database (RAG features)
- **[OpenAI](https://openai.com)** - Embedding generation API (RAG features)

### Inspired By

- **[AWS Q Developer](https://aws.amazon.com/q/developer/)** - AI coding assistant with local filesystem operations (inspired our fs_read approach)
- **[Serena](https://github.com/oraios/serena)** - Code intelligence and semantic search
- **[Continue](https://github.com/continuedev/continue)** - AI-powered code assistant
- **[Tabby](https://github.com/TabbyML/tabby)** - Self-hosted AI coding assistant
- **[Semantic Code Search](https://github.com/sturdy-dev/semantic-code-search)** - Code search and retrieval
- **[Aider](https://github.com/Aider-AI/aider)** - AI pair programming in the terminal
- **[VS Code Copilot Chat](https://github.com/microsoft/vscode-copilot-chat)** - Conversational AI for code

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/starthackHQ/Contextinator/blob/main/LICENSE) for details.

<h1 align="left">TL;DR <img src="https://raw.githubusercontent.com/starthackHQ/Contextinator/main/docs/0banner.png" alt="Contextinator" width="30" /></h1>

Contextinator is a **Rust-powered filesystem toolkit** designed for AI agents to efficiently read files, explore directories, and search codebases with blazing-fast performance. It provides local filesystem operations inspired by AWS Q Developer's approach, prioritizing speed and simplicity over embedding-based solutions. Additionally, it offers optional RAG capabilities using Abstract Syntax Tree (AST) parsing to extract semantic code chunks, generate embeddings, and enable advanced code intelligence for deeper codebase understanding.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=starthackHQ/Contextinator&type=Date)](https://star-history.com/#starthackHQ/Contextinator&Date)
