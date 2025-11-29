<img src="./docs/banner.webp" alt="Contextinator" width="100%" />
<br />
<p align="center">
Turn any codebase into semantically-aware, searchable knowledge for AI-powered workflows.
</p>

### Key Features

- **AST-Powered Chunking** - Extract functions, classes, and methods from 23+ programming languages
- **Parent-Child Relationships** - Maintain hierarchical chunk-context for complete understanding
- **Semantic Search** - Find relevant code using natural language queries
- **Multiple Search Modes** - Semantic, symbol-based, pattern matching, and hybrid search
- **Smart Deduplication** - Hash-based detection of duplicate code
- **TOON Format Export** - Token-efficient output format for LLM prompts (40-60% token savings)
- **Full Pipeline Automation** - One command to chunk, embed, and store
- **Docker-Ready** - ChromaDB server included

### Use Cases

| **Agentic AI Systems**                              | **RAG Applications**                                     | **Code Intelligence**                      |
| --------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------ |
| Dynamic code retrieval for autonomous coding agents | High-precision code retrieval for question answering     | Cross-repository code search and discovery |
| Context provision for code generation               | Context injection for code explanation and documentation | Duplicate and similar code detection       |
| Multi-step reasoning over large codebases           | Semantic code search across repositories                 | Legacy codebase analysis and understanding |
| Tool integration for agent frameworks               | Parent-child relationship tracking for complete context  | MCP-compliant async architecture           |

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker (for ChromaDB)
- OpenAI API key (for embeddings)

### Installation
```bash
pip install contextinator
```

Verify the installation _(requiers chromadb & openai api key setup)_:

```bash
contextinator --help
```

For detailed setup and configuration, see [`USAGE.md`](USAGE.md)

### Getting Started

1. Index a repository:

```bash
contextinator chunk-embed-store-embeddings \
  --repo-url https://github.com/user/repo \
  --save \
  --collection-name MyRepo
```

2. Search your codebase:

```bash
# Natural language semantic search
contextinator search "authentication logic" -c MyRepo

# Find specific functions
contextinator symbol authenticate_user -c MyRepo

# Export results in TOON format for LLM consumption
contextinator search "error handling" -c MyRepo --toon results.json
```

For comprehensive CLI and Python API documentation, see [`USAGE.md`](USAGE.md)

## Acknowledgements

- **[tree-sitter](https://github.com/tree-sitter/tree-sitter)** - Incremental parsing system for AST generation
- **[ChromaDB](https://github.com/chroma-core/chroma)** - AI-native embedding database
- **[OpenAI](https://openai.com)** - Embedding generation API
- **[Vs-code-copilotchat](https://github.com/microsoft/vscode-copilotchat)** - overall architecture inspiration
- **[Continue.dev](https://continue.dev)** - chunking and embedding pipeline inspiration

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

<h1 align="left">TL;DR <img src="./docs/0banner.png" alt="Contextinator" width="30" /></h1>

Contextinator is a code intelligence tool that uses Abstract Syntax Tree (AST) parsing to extract semantic code chunks, generates embeddings, and stores them in a vector database. This enables AI systems to understand, navigate, and reason about codebases with precision.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=starthackHQ/Contextinator&type=Date)](https://star-history.com/#starthackHQ/Contextinator&Date)
