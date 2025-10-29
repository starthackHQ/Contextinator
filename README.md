# Code Semantic Search Experiment

This repository contains an experimental setup for performing semantic search on a code base. The goal is to enable efficient and accurate retrieval of code snippets based on natural language queries.

# Project Setup

1. Clone the repository
2. Set up a Python virtual environment using `python -m venv .venv`
3. Activate the virtual environment:
   - On Windows: `.venv\Scripts\activate`
   - On macOS/Linux: `source .venv/bin/activate`

# Usage

The project provides a CLI tool called `semanticsage` for semantic code search operations. Run commands from the project root using:

```bash
python -m src.cli <command> [options]
```

## Available Commands

### `chunk --save`

Chunks the local Git codebase into semantic units (e.g., functions or classes) and stores them in a `.chunks` folder for further processing. Optionally generates AST visualizations for code analysis.

```bash
python -m src.cli chunk --save
python -m src.cli chunk --save --save-ast --ast-output-dir ./analysis
python -m src.cli chunk --save --repo-url https://github.com/user/repo
```

### `embed --save`

Generates embeddings for the existing chunks using a specified model and saves them in a `.embeddings` folder.

```bash
python -m src.cli embed --save
python -m src.cli embed --save --model-name-or-path your-model --batch-size 16
```

### `store-embeddings --vectorstore chroma`

Loads the embeddings into a vector store like Chroma for persistent querying, using a local database path.

```bash
python -m src.cli store-embeddings --vectorstore chroma
python -m src.cli store-embeddings --vectorstore chroma --db-path .chroma_db
```

### `chunk-embed-store-embeddings`

Executes the full pipeline of chunking, embedding, and storing in one command, creating all necessary folders and the vector database. Supports AST analysis integration.

```bash
python -m src.cli chunk-embed-store-embeddings --save --vectorstore chroma
python -m src.cli chunk-embed-store-embeddings --save --vectorstore chroma --save-ast
```

### `query`

Performs a semantic search on the vector store, returning top relevant code chunks with similarity scores and file references.

```bash
python -m src.cli query "implement user authentication in Python"
python -m src.cli query "myquery" --save results.txt --n-results 10
```

## Command Options

- `--save`: Save intermediate artifacts (chunks, embeddings) to local folders
- `--vectorstore`: Choose vector store backend (currently supports `chroma`)
- `--db-path`: Specify local path for vector database storage
- `--model-name-or-path`: Specify the embedding model to use
- `--batch-size`: Set batch size for embedding generation
- `--n-results`: Number of search results to return
- `--save FILE`: Save query results to a specified file
- `--save-ast`: Generate and save AST visualizations and analysis data
- `--ast-output-dir DIR`: Specify directory for AST output (default: `.ast_output`)
- `--repo-url URL`: Process a remote Git repository by cloning it first
- `--max-tokens N`: Set maximum tokens per chunk for embedding compatibility

## Examples

```bash
# Full workflow: chunk, embed, and store in one command
python -m src.cli chunk-embed-store-embeddings --save --vectorstore chroma

# Search for authentication-related code
python -m src.cli query "user authentication login" --n-results 5

# Save search results to a file
python -m src.cli query "database connection" --save db_results.txt
```

## Advanced Options

### AST Visualization and Analysis

The project includes advanced features for Abstract Syntax Tree (AST) analysis and visualization, powered by Tree-sitter parsers for multiple programming languages.

#### Save AST Data During Chunking

Generate detailed AST visualizations and metadata while chunking your codebase:

```bash
# Save AST data and visualizations during chunking
python -m src.cli chunk --save --save-ast

# Specify custom output directory for AST data
python -m src.cli chunk --save --save-ast --ast-output-dir ./ast_analysis
```

#### AST Output Structure

When `--save-ast` is enabled, the tool creates detailed AST analysis files in the specified output directory (defaults to `.ast_output`):

```
.ast_output/
├── summary.json              # Overall analysis summary
├── file_stats.json          # Per-file statistics
└── files/
    ├── path_to_file_1.json  # Individual file AST data
    ├── path_to_file_2.json
    └── ...
```

Each file's AST data includes:

- **Tree Structure**: Complete AST hierarchy with node types and relationships
- **Semantic Nodes**: Extracted functions, classes, methods, and other code constructs
- **Metadata**: File statistics, tree depth, node counts, and parsing information
- **Source Mapping**: Line numbers, byte positions, and content mappings


#### Advanced Command Options

- `--save-ast`: Enable AST data generation and saving
- `--ast-output-dir DIR`: Specify custom directory for AST output (default: `.ast_output`)
- `--repo-url URL`: Process a remote repository by cloning it first
- `--max-tokens N`: Set maximum tokens per chunk for embedding compatibility

#### Example Workflows

```bash
# Analyze a local repository with AST visualization
python -m src.cli chunk --save --save-ast

# Analyze a remote repository with custom AST output location
python -m src.cli chunk --save --save-ast --repo-url https://github.com/iamDyeus/suppap --ast-output-dir ./analysis

# Full pipeline with AST analysis
python -m src.cli chunk-embed-store-embeddings --save --vectorstore chroma --save-ast
```


# Installation

```
pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript tree-sitter-java tree-sitter-go tree-sitter-rust tree-sitter-cpp tree-sitter-c chromadb
```
