import argparse
import sys
from .utils import resolve_repo_path, logger
import os    
from .chunking import chunk_repository

def chunk_func(args):
    from pathlib import Path
    from .utils.repo_utils import extract_repo_name_from_url
    
    repo_url = getattr(args, 'repo_url', None)
    
    repo_path = resolve_repo_path(
        repo_url=repo_url,
        path=getattr(args, 'path', None)
    )
    
    # Determine repository name
    # If cloned from URL, extract name from URL instead of temp directory name
    if repo_url:
        repo_name = extract_repo_name_from_url(repo_url)
    else:
        repo_name = Path(repo_path).name
    
    # Use output dir if specified, otherwise current directory
    output_dir = getattr(args, 'output', None) or os.getcwd()
    
    # Check if AST saving is requested
    save_ast = getattr(args, 'save_ast', False)
    
    chunks = chunk_repository(
        repo_path=repo_path,
        repo_name=repo_name,
        save=args.save, 
        output_dir=output_dir, 
        save_ast=save_ast
    )
    logger.info("✅ Chunking complete: {len(chunks)} chunks created")
    
    if args.save:
        logger.info("Chunks saved in: {output_dir}/.chunks/{repo_name}/")
    
    if save_ast:
        logger.info("AST trees saved for analysis")
        logger.info("Check: {output_dir}/.chunks/{repo_name}/ast_trees/ for AST files")


def embed_func(args):
    """Generate embeddings for existing chunks."""
    from .embedding import embed_chunks
    from .utils import resolve_repo_path, logger
    from .utils.repo_utils import extract_repo_name_from_url
    from pathlib import Path
    import os
    
    try:
        repo_url = getattr(args, 'repo_url', None)
        
        repo_path = resolve_repo_path(
            repo_url=repo_url,
            path=getattr(args, 'path', None)
        )
        
        # Determine repository name
        if repo_url:
            repo_name = extract_repo_name_from_url(repo_url)
        else:
            repo_name = Path(repo_path).name
        
        base_dir = getattr(args, 'output', None) or os.getcwd()
        
        logger.info("Generating embeddings for repository: {repo_name}")
        
        # Generate embeddings
        embedded_chunks = embed_chunks(base_dir, repo_name, save=args.save)
        
        logger.info("Embedding generation complete: {len(embedded_chunks)} chunks embedded")
        
        if args.save:
            logger.info("Embeddings saved to {base_dir}/.embeddings/{repo_name}/")
        
    except Exception as e:
        logger.error("Embedding generation failed: {str(e)}")
        exit(1)


def store_embeddings_func(args):
    """Store embeddings in ChromaDB vector store."""
    from .embedding import load_embeddings
    from .vectorstore import store_repository_embeddings
    from .utils import resolve_repo_path, logger
    from .utils.repo_utils import extract_repo_name_from_url
    from pathlib import Path
    import os
    
    try:
        repo_url = getattr(args, 'repo_url', None)
        
        repo_path = resolve_repo_path(
            repo_url=repo_url,
            path=getattr(args, 'path', None)
        )
        
        # Determine repository name
        if repo_url:
            repo_name = extract_repo_name_from_url(repo_url)
        else:
            repo_name = Path(repo_path).name
        
        base_dir = getattr(args, 'output', None) or os.getcwd()
        
        logger.info("Storing embeddings for repository: {repo_name}")
        
        # Load embeddings
        embedded_chunks = load_embeddings(base_dir, repo_name)
        
        # Determine collection name
        collection_name = getattr(args, 'collection_name', None) or repo_name
        
        # Store in ChromaDB
        stats = store_repository_embeddings(base_dir, repo_name, embedded_chunks, collection_name)
        
        logger.info("Storage complete:")
        logger.info("   📊 Stored: %d embeddings", stats["stored_count"])
        logger.info("   📚 Collection: %s", stats["collection_name"])
        logger.info("   🗄️  Database: %s", stats["db_path"])
        
    except Exception as e:
        logger.error("Embedding storage failed: {str(e)}")
        exit(1)


def pipeline_func(args):
    """Combined chunk + embed + store-embeddings pipeline."""
    from .embedding import embed_chunks
    from .vectorstore import store_repository_embeddings
    from .utils import resolve_repo_path, logger
    from .utils.repo_utils import extract_repo_name_from_url
    from pathlib import Path
    import os
    
    try:
        repo_url = getattr(args, 'repo_url', None)
        
        repo_path = resolve_repo_path(
            repo_url=repo_url,
            path=getattr(args, 'path', None)
        )
        
        # Determine repository name
        if repo_url:
            repo_name = extract_repo_name_from_url(repo_url)
        else:
            repo_name = Path(repo_path).name
        
        base_dir = getattr(args, 'output', None) or os.getcwd()
        
        logger.info("Starting complete pipeline for repository: {repo_name}")
        
        # Step 1: Chunk repository
        logger.info("\n📝 Step 1: Chunking repository...")
        chunks = chunk_repository(
            repo_path=repo_path,
            repo_name=repo_name,
            save=args.save,
            output_dir=base_dir
        )
        
        if not chunks:
            logger.info("❌ No chunks generated. Pipeline stopped.")
            exit(1)
        
        # Step 2: Generate embeddings
        logger.info("\n🧠 Step 2: Generating embeddings...")
        embedded_chunks = embed_chunks(base_dir, repo_name, save=args.save, chunks_data=chunks)
        
        # Step 3: Store in vector database
        logger.info("\n🗄️  Step 3: Storing in vector database...")
        collection_name = getattr(args, 'collection_name', None) or repo_name
        stats = store_repository_embeddings(base_dir, repo_name, embedded_chunks, collection_name)
        
        logger.info("✅ Pipeline complete!")
        logger.info("   📝 Chunks: %d", len(chunks))
        logger.info("   🧠 Embeddings: %d", len(embedded_chunks))
        logger.info("   📊 Stored: %d", stats["stored_count"])
        logger.info("   📚 Collection: %s", stats["collection_name"])
        logger.info("   🗄️  Database: %s", stats["db_path"])
        
        if args.save:
            logger.info("   💾 Artifacts saved in: %s/.chunks/%s/ and %s/.embeddings/%s/", base_dir, repo_name, base_dir, repo_name)
        
    except Exception as e:
        logger.error("Pipeline failed: {str(e)}")
        exit(1)


def query_func(args):
    logger.info("query this functionality")
    pass


# ============================================================================
# SEARCH TOOL COMMANDS
# ============================================================================

def search_func(args):
    """Semantic search using natural language queries."""
    from .tools import semantic_search
    from .utils.output_formatter import format_search_results, export_json
    
    try:
        query = ' '.join(args.query_text) if isinstance(args.query_text, list) else args.query_text
        
        results = semantic_search(
            collection_name=args.collection,
            query=query,
            n_results=args.n_results,
            language=getattr(args, 'language', None),
            file_path=getattr(args, 'file', None),
            node_type=getattr(args, 'type', None)
        )
        
        if args.json:
            export_json({
                'query': query,
                'collection': args.collection,
                'total_results': len(results),
                'results': results
            }, args.json)
        else:
            format_search_results(results, query=query, collection=args.collection)
        
    except Exception as e:
        logger.error("Search failed: {e}")
        exit(1)


def symbol_func(args):
    """Find symbols (functions/classes) by name."""
    from .tools import symbol_search
    from .utils.output_formatter import format_search_results, export_json
    
    try:
        results = symbol_search(
            collection_name=args.collection,
            symbol_name=args.symbol_name,
            node_type=getattr(args, 'type', None),
            file_path=getattr(args, 'file', None),
            limit=args.limit
        )
        
        if args.json:
            export_json({
                'symbol': args.symbol_name,
                'collection': args.collection,
                'total_results': len(results),
                'results': results
            }, args.json)
        else:
            format_search_results(results, query=f"Symbol: {args.symbol_name}", collection=args.collection)
        
    except Exception as e:
        logger.error("Symbol search failed: {e}")
        exit(1)


def pattern_func(args):
    """Search for code patterns using regex."""
    from .tools import regex_search
    from .utils.output_formatter import format_search_results, export_json
    
    try:
        results = regex_search(
            collection_name=args.collection,
            pattern=args.pattern,
            language=getattr(args, 'language', None),
            file_path=getattr(args, 'file', None),
            node_type=getattr(args, 'type', None),
            limit=args.limit
        )
        
        if args.json:
            export_json({
                'pattern': args.pattern,
                'collection': args.collection,
                'total_results': len(results),
                'results': results
            }, args.json)
        else:
            format_search_results(results, query=f"Pattern: {args.pattern}", collection=args.collection)
        
    except Exception as e:
        logger.error("Pattern search failed: {e}")
        exit(1)


def read_file_func(args):
    """Reconstruct and display complete file from chunks."""
    from .tools import read_file
    from .utils.output_formatter import format_file_content, export_json
    
    try:
        file_data = read_file(
            collection_name=args.collection,
            file_path=args.file_path,
            join_chunks=not args.no_join
        )
        
        if args.json:
            export_json(file_data, args.json)
        else:
            format_file_content(file_data)
        
    except Exception as e:
        logger.error("Read file failed: {e}")
        exit(1)


def search_advanced_func(args):
    """Advanced search with multiple criteria."""
    from .tools import hybrid_search, full_text_search
    from .utils.output_formatter import format_search_results, export_json
    
    try:
        # Use hybrid search if semantic query provided
        if args.semantic:
            filters = {}
            if args.language:
                filters['language'] = args.language
            if args.file:
                filters['file_path'] = {'$contains': args.file}
            if args.type:
                filters['node_type'] = args.type
            
            results = hybrid_search(
                collection_name=args.collection,
                semantic_query=args.semantic,
                metadata_filters=filters if filters else None,
                n_results=args.limit
            )
            query_desc = f"Hybrid: {args.semantic}"
        else:
            # Use full text search
            where = {}
            if args.language:
                where['language'] = args.language
            if args.file:
                where['file_path'] = {'$contains': args.file}
            if args.type:
                where['node_type'] = args.type
            
            results = full_text_search(
                collection_name=args.collection,
                text_pattern=args.pattern,
                where=where if where else None,
                limit=args.limit
            )
            query_desc = f"Advanced: {args.pattern or 'metadata filters'}"
        
        if args.json:
            export_json({
                'query': query_desc,
                'collection': args.collection,
                'total_results': len(results),
                'results': results
            }, args.json)
        else:
            format_search_results(results, query=query_desc, collection=args.collection)
        
    except Exception as e:
        logger.error("Advanced search failed: {e}")
        exit(1)


def db_info_func(args):
    """Show ChromaDB database information."""
    from .vectorstore import ChromaVectorStore
    import os
    from pathlib import Path
    
    try:
        # Use output directory if provided, otherwise current directory
        base_dir = getattr(args, 'output', None) or os.getcwd()
        repo_name = getattr(args, 'repo_name', None) or Path(base_dir).name
        
        vector_store = ChromaVectorStore(base_dir=base_dir, repo_name=repo_name)
        collections = vector_store.list_collections()
        
        logger.info("ChromaDB Database Information")
        logger.info("Database path: {vector_store.db_path}")
        logger.info("=" * 50)
        
        if not collections:
            logger.info("📭 No collections found in the database")
            return
        
        logger.info("Found {len(collections)} collection(s):")
        logger.info("")
        
        for collection in collections:
            logger.info("  📖 Collection: %s", collection["name"])
            logger.info("     📊 Documents: %d", collection["count"])
            if collection.get('metadata'):
                logger.info("     📝 Description: %s", collection["metadata"].get("description", "N/A"))
            logger.info("")
        
        # Show total documents
        total_docs = sum(col['count'] for col in collections)
        logger.info("Total documents across all collections: {total_docs}")
        
    except Exception as e:
        logger.error("Failed to get database info: {str(e)}")
        exit(1)


def db_list_func(args):
    """List all collections in ChromaDB."""
    from .vectorstore import ChromaVectorStore
    import os
    from pathlib import Path
    
    try:
        # Use output directory if provided, otherwise current directory
        base_dir = getattr(args, 'output', None) or os.getcwd()
        repo_name = getattr(args, 'repo_name', None) or Path(base_dir).name
        
        vector_store = ChromaVectorStore(base_dir=base_dir, repo_name=repo_name)
        collections = vector_store.list_collections()
        
        logger.info("Database path: {vector_store.db_path}")
        
        if not collections:
            logger.info("📭 No collections found")
            return
        
        logger.info("📚 Collections:")
        for collection in collections:
            logger.info("  - %s (%d documents)", collection["name"], collection["count"])
        
    except Exception as e:
        logger.error("Failed to list collections: {str(e)}")
        exit(1)


def db_show_func(args):
    """Show details of a specific collection."""
    from .vectorstore import ChromaVectorStore
    from .config import sanitize_collection_name
    import os
    from pathlib import Path
    
    try:
        # Use output directory if provided, otherwise current directory
        base_dir = getattr(args, 'output', None) or os.getcwd()
        repo_name = getattr(args, 'repo_name', None) or Path(base_dir).name
        
        collection_name = args.collection_name
        vector_store = ChromaVectorStore(base_dir=base_dir, repo_name=repo_name)
        
        logger.info("Database path: {vector_store.db_path}")
        
        # Get collection info
        info = vector_store.get_collection_info(collection_name)
        
        if not info.get('exists', True):
            logger.error("Collection '{collection_name}' not found")
            return
        
        logger.info("Collection: {info['name']}")
        logger.info("Documents: {info['count']}")
        if info.get('metadata'):
            logger.info("Description: {info['metadata'].get('description', 'N/A')}")
        
        # Get a few sample documents if requested
        if args.sample and info['count'] > 0:
            try:
                safe_name = sanitize_collection_name(collection_name)
                collection = vector_store.client.get_collection(name=safe_name)
                
                # Get first few documents
                sample_size = min(args.sample, info['count'])
                results = collection.get(limit=sample_size)
                
                logger.info("📄 Sample documents (showing {sample_size}):")
                for i, (doc_id, document, metadata) in enumerate(zip(
                    results['ids'], results['documents'], results['metadatas']
                )):
                    logger.info("  Document {i+1}:")
                    logger.info("    ID: %s", doc_id)
                    logger.info("    Content: %s%s", document[:200], "..." if len(document) > 200 else "")
                    if metadata:
                        logger.info("    Metadata: %s", metadata)
                        
            except Exception as e:
                logger.warning("Could not fetch sample documents: {str(e)}")
        
    except Exception as e:
        logger.error("Failed to show collection: {str(e)}")
        exit(1)


def db_clear_func(args):
    """Clear/delete a specific collection."""
    from .vectorstore import ChromaVectorStore
    from .config import sanitize_collection_name
    import os
    from pathlib import Path
    
    try:
        # Use output directory if provided, otherwise current directory
        base_dir = getattr(args, 'output', None) or os.getcwd()
        repo_name = getattr(args, 'repo_name', None) or Path(base_dir).name
        
        collection_name = args.collection_name
        vector_store = ChromaVectorStore(base_dir=base_dir, repo_name=repo_name)
        
        logger.info("Database path: {vector_store.db_path}")
        
        # Confirm deletion
        if not args.force:
            response = input(f"⚠️  Are you sure you want to delete collection '{collection_name}'? (y/N): ")
            if response.lower() != 'y':
                logger.info("❌ Operation cancelled")
                return
        
        # Delete collection
        safe_name = sanitize_collection_name(collection_name)
        try:
            vector_store.client.delete_collection(name=safe_name)
            logger.info("Collection '{collection_name}' deleted successfully")
        except Exception as e:
            logger.error("Failed to delete collection: {str(e)}")
            exit(1)
        
    except Exception as e:
        logger.error("Failed to clear collection: {str(e)}")
        exit(1)


def main():
    parser = argparse.ArgumentParser(prog='contextinator', description='Contextinator — semantic codebase tooling')

    sub = parser.add_subparsers(title='commands', dest='command')

    # chunk
    p_chunk = sub.add_parser('chunk', help='Chunks the local Git codebase into semantic units and (optionally) save them')
    p_chunk.add_argument('--save', action='store_true', help='Save chunks to a .chunks folder')
    p_chunk.add_argument('--save-ast', action='store_true', help='Save AST trees for analysis and debugging')
    p_chunk.add_argument('--repo-url', help='GitHub/Git repository URL to clone and chunk')
    p_chunk.add_argument('--path', help='Local path to repository (default: current directory)')
    p_chunk.add_argument('--output', '-o', help='Output directory for chunks (default: current directory)')
    p_chunk.set_defaults(func=chunk_func)

    # embed
    p_embed = sub.add_parser('embed', help='Generate embeddings for existing chunks using OpenAI and (optionally) save them')
    p_embed.add_argument('--save', action='store_true', help='Save embeddings to a .embeddings folder')
    p_embed.add_argument('--repo-url', help='GitHub/Git repository URL to clone and embed')
    p_embed.add_argument('--path', help='Local path to repository (default: current directory)')
    p_embed.add_argument('--output', '-o', help='Base directory containing .chunks folder (default: current directory)')
    p_embed.set_defaults(func=embed_func)

    # store-embeddings
    p_store = sub.add_parser('store-embeddings', help='Load embeddings into ChromaDB vector store')
    p_store.add_argument('--repo-url', help='GitHub/Git repository URL')
    p_store.add_argument('--path', help='Local path to repository (default: current directory)')
    p_store.add_argument('--output', '-o', help='Base directory containing .embeddings folder (default: current directory)')
    p_store.add_argument('--collection-name', help='Custom collection name (default: repository name)')
    p_store.set_defaults(func=store_embeddings_func)

    # combined pipeline: chunk-embed-store-embeddings
    p_pipeline = sub.add_parser('chunk-embed-store-embeddings', help='Run chunk, embed and store-embeddings in a single command')
    p_pipeline.add_argument('--save', action='store_true', help='Save intermediate artifacts (chunks + embeddings)')
    p_pipeline.add_argument('--repo-url', help='GitHub/Git repository URL to clone and process')
    p_pipeline.add_argument('--path', help='Local path to repository (default: current directory)')
    p_pipeline.add_argument('--output', '-o', help='Base output directory (default: current directory)')
    p_pipeline.add_argument('--collection-name', help='Custom collection name (default: repository name)')
    p_pipeline.set_defaults(func=pipeline_func)

    # query
    p_query = sub.add_parser('query', help='Query the vector store for semantically similar code chunks')
    p_query.add_argument('query_text', nargs=argparse.REMAINDER, help='Query text (wrap in quotes if multiple words)')
    p_query.add_argument('--n-results', '-n', type=int, default=5, help='Number of results to return')
    p_query.add_argument('--save', metavar='FILE', help='Save results to a file (JSON or text)')
    p_query.set_defaults(func=query_func)

    # db-info
    p_db_info = sub.add_parser('db-info', help='Show ChromaDB database information and statistics')
    p_db_info.set_defaults(func=db_info_func)

    # db-list
    p_db_list = sub.add_parser('db-list', help='List all collections in ChromaDB')
    p_db_list.set_defaults(func=db_list_func)

    # db-show
    p_db_show = sub.add_parser('db-show', help='Show details of a specific collection')
    p_db_show.add_argument('collection_name', help='Name of the collection to show')
    p_db_show.add_argument('--sample', type=int, default=0, help='Show sample documents (specify number)')
    p_db_show.set_defaults(func=db_show_func)

    # db-clear
    p_db_clear = sub.add_parser('db-clear', help='Delete a specific collection')
    p_db_clear.add_argument('collection_name', help='Name of the collection to delete')
    p_db_clear.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    p_db_clear.set_defaults(func=db_clear_func)

    # ========================================================================
    # SEARCH TOOL COMMANDS
    # ========================================================================

    # search (semantic search)
    p_search = sub.add_parser('search', help='Semantic search using natural language queries')
    p_search.add_argument('query_text', nargs='+', help='Natural language query')
    p_search.add_argument('--collection', '-c', required=True, help='Collection name')
    p_search.add_argument('--n-results', '-n', type=int, default=5, help='Number of results (default: 5)')
    p_search.add_argument('--language', '-l', help='Filter by programming language')
    p_search.add_argument('--file', '-f', help='Filter by file path (partial match)')
    p_search.add_argument('--type', '-t', help='Filter by node type')
    p_search.add_argument('--json', help='Export results to JSON file')
    p_search.set_defaults(func=search_func)

    # symbol (symbol search)
    p_symbol = sub.add_parser('symbol', help='Find symbols (functions/classes) by name')
    p_symbol.add_argument('symbol_name', help='Symbol name to search for')
    p_symbol.add_argument('--collection', '-c', required=True, help='Collection name')
    p_symbol.add_argument('--type', '-t', help='Filter by node type')
    p_symbol.add_argument('--file', '-f', help='Filter by file path (partial match)')
    p_symbol.add_argument('--limit', type=int, default=50, help='Maximum results (default: 50)')
    p_symbol.add_argument('--json', help='Export results to JSON file')
    p_symbol.set_defaults(func=symbol_func)

    # pattern (regex search)
    p_pattern = sub.add_parser('pattern', help='Search for code patterns')
    p_pattern.add_argument('pattern', help='Text pattern to search for')
    p_pattern.add_argument('--collection', '-c', required=True, help='Collection name')
    p_pattern.add_argument('--language', '-l', help='Filter by programming language')
    p_pattern.add_argument('--file', '-f', help='Filter by file path (partial match)')
    p_pattern.add_argument('--type', '-t', help='Filter by node type')
    p_pattern.add_argument('--limit', type=int, default=50, help='Maximum results (default: 50)')
    p_pattern.add_argument('--json', help='Export results to JSON file')
    p_pattern.set_defaults(func=pattern_func)

    # read-file (file reconstruction)
    p_read_file = sub.add_parser('read-file', help='Reconstruct and display complete file from chunks')
    p_read_file.add_argument('file_path', help='File path to read')
    p_read_file.add_argument('--collection', '-c', required=True, help='Collection name')
    p_read_file.add_argument('--no-join', action='store_true', help='Show chunks separately (don\'t join)')
    p_read_file.add_argument('--json', help='Export to JSON file')
    p_read_file.set_defaults(func=read_file_func)

    # search-advanced (advanced/hybrid search)
    p_search_adv = sub.add_parser('search-advanced', help='Advanced search with multiple criteria')
    p_search_adv.add_argument('--collection', '-c', required=True, help='Collection name')
    p_search_adv.add_argument('--semantic', '-s', help='Semantic query for hybrid search')
    p_search_adv.add_argument('--pattern', '-p', help='Text pattern to search for')
    p_search_adv.add_argument('--language', '-l', help='Filter by programming language')
    p_search_adv.add_argument('--file', '-f', help='Filter by file path (partial match)')
    p_search_adv.add_argument('--type', '-t', help='Filter by node type')
    p_search_adv.add_argument('--limit', type=int, default=50, help='Maximum results (default: 50)')
    p_search_adv.add_argument('--json', help='Export results to JSON file')
    p_search_adv.set_defaults(func=search_advanced_func)

    args = parser.parse_args()

    # If no subcommand was provided, show help and exit
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    # Call the selected subcommand handler
    args.func(args)


if __name__ == '__main__':
    main()
