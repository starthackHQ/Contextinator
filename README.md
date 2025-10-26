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

Chunks the local Git codebase into semantic units (e.g., functions or classes) and stores them in a `.chunks` folder for further processing.

```bash
python -m src.cli chunk --save
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

Executes the full pipeline of chunking, embedding, and storing in one command, creating all necessary folders and the vector database.

```bash
python -m src.cli chunk-embed-store-embeddings --save --vectorstore chroma
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

## Examples

```bash
# Full workflow: chunk, embed, and store in one command
python -m src.cli chunk-embed-store-embeddings --save --vectorstore chroma

# Search for authentication-related code
python -m src.cli query "user authentication login" --n-results 5

# Save search results to a file
python -m src.cli query "database connection" --save db_results.txt
```
