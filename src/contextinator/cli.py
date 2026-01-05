import argparse
import sys
from .utils import resolve_repo_path, logger
from .utils.exceptions import FileSystemError
from .utils.rich_help import print_main_help, RichHelpFormatter
import os    
from .chunking import chunk_repository
from .config import get_storage_path

def chunk_func(args):
    from pathlib import Path
    from .utils.repo_utils import extract_repo_name_from_url
    
    repo_url = getattr(args, 'repo_url', None)
    
    try:
        repo_path = resolve_repo_path(
            repo_url=repo_url,
            path=getattr(args, 'path', None)
        )
    except FileSystemError as e:
        logger.error(str(e))
        sys.exit(1)
    
    # Determine repository name
    # If cloned from URL, extract name from URL instead of temp directory name
    if repo_url:
        repo_name = extract_repo_name_from_url(repo_url)
    else:
        repo_name = Path(repo_path).name
    
    # Use output dir if specified, otherwise current directory
    output_dir = getattr(args, 'output', None) or os.getcwd()
    
    # Get custom chunks directory if specified
    custom_chunks_dir = getattr(args, 'chunks_dir', None)    # Check if AST saving is requested
    save_ast = getattr(args, 'save_ast', False)
    
    chunks = chunk_repository(
        repo_path=repo_path,
        repo_name=repo_name,
        save=args.save, 
        output_dir=output_dir, 
        save_ast=save_ast,
        custom_chunks_dir=custom_chunks_dir
    )
    logger.info(f"✅ Chunking complete: {len(chunks)} chunks created")
    
    if args.save:
        chunks_path = get_storage_path(output_dir, 'chunks', repo_name, custom_chunks_dir)
        logger.info(f"Chunks saved in: {chunks_path}/")
    
    if save_ast:
        logger.info("AST trees saved for analysis")
        chunks_path = get_storage_path(output_dir, 'chunks', repo_name, custom_chunks_dir)
        logger.info(f"Check: {chunks_path}/ast_trees/ for AST files")


def embed_func(args):
    """Generate embeddings for existing chunks."""
    from .embedding import embed_chunks
    from .utils import resolve_repo_path, logger
    from .utils.repo_utils import extract_repo_name_from_url
    from pathlib import Path
    import os
    # Set API key if provided
    
    if hasattr(args, 'api_key') and args.api_key:
        os.environ['OPENAI_API_KEY'] = args.api_key
         
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
        # Get custom directory arguments
        custom_chunks_dir = getattr(args, 'chunks_dir', None)
        custom_embeddings_dir = getattr(args, 'embeddings_dir', None)
        logger.info(f"Generating embeddings for repository: {repo_name}")
        
        # Generate embeddings
        embedded_chunks = embed_chunks(base_dir, repo_name, save=args.save,
                                      custom_chunks_dir=custom_chunks_dir,
                                      custom_embeddings_dir=custom_embeddings_dir)
        
        logger.info(f"Embedding generation complete: {len(embedded_chunks)} chunks embedded")
        
        if args.save:
            embeddings_path = get_storage_path(base_dir, 'embeddings', repo_name, custom_embeddings_dir)
            logger.info(f"Embeddings saved to {embeddings_path}/")
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        exit(1)




def structure_func(args):
    """Analyze and display repository structure."""
    import asyncio
    from .tools.repo_structure import analyze_structure_async
    from .utils import resolve_repo_path, logger
    
    try:
        repo_url = getattr(args, 'repo_url', None)
        
        repo_path = resolve_repo_path(
            repo_url=repo_url,
            path=getattr(args, 'path', None)
        )
        
        max_depth = getattr(args, 'depth', None)
        output_format = getattr(args, 'format', 'tree')
        output_file = getattr(args, 'output', None)
        
        structure = asyncio.run(analyze_structure_async(
            repo_path=repo_path,
            max_depth=max_depth,
            output_format=output_format,
            output_file=output_file
        ))
        
        print(structure)
        
    except Exception as e:
        logger.error(f"Structure analysis failed: {str(e)}")
        sys.exit(1)


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
        elif getattr(args, 'repo_name', None):
            repo_name = args.repo_name
        else:
            repo_name = Path(repo_path).name
        
        base_dir = getattr(args, 'output', None) or os.getcwd()
        # Get custom directory arguments
        custom_embeddings_dir = getattr(args, 'embeddings_dir', None)
        custom_chromadb_dir = getattr(args, 'chromadb_dir', None)
        logger.info(f"Storing embeddings for repository: {repo_name}")
        
        # Load embeddings
        embedded_chunks = load_embeddings(base_dir, repo_name, custom_embeddings_dir)
        
        # Determine collection name
        collection_name = getattr(args, 'collection_name', None) or repo_name
        
        # Store in ChromaDB
        stats = store_repository_embeddings(base_dir, repo_name, embedded_chunks, collection_name, custom_chromadb_dir)
        
        logger.info("Storage complete:")
        logger.info("   📊 Stored: %d embeddings", stats["stored_count"])
        logger.info("   📚 Collection: %s", stats["collection_name"])
        if "db_path" in stats:  # Only show when using local persistence
            logger.info("   🗄️  Database: %s", stats["db_path"])
        else:
            logger.info("   🌐 Saved in ChromaDB server")
        
    except Exception as e:
        logger.error(f"Embedding storage failed: {str(e)}")
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
        
        # Get custom directory arguments
        custom_chunks_dir = getattr(args, 'chunks_dir', None)
        custom_embeddings_dir = getattr(args, 'embeddings_dir', None)
        custom_chromadb_dir = getattr(args, 'chromadb_dir', None)
        base_dir = getattr(args, 'output', None) or os.getcwd()
        
        logger.info(f"Starting complete pipeline for repository: {repo_name}")
        
        # Step 1: Chunk repository
        logger.info("\n📝 Step 1: Chunking repository...")
        chunks = chunk_repository(
            repo_path=repo_path,
            repo_name=repo_name,
            save=args.save,
            output_dir=base_dir,
            custom_chunks_dir=custom_chunks_dir
        )
        
        if not chunks:
            logger.info("❌ No chunks generated. Pipeline stopped.")
            exit(1)
        
        # Step 2: Generate embeddings
        logger.info("\n🧠 Step 2: Generating embeddings...")
        embedded_chunks = embed_chunks(base_dir, repo_name, save=args.save, chunks_data=chunks,
                                      custom_chunks_dir=custom_chunks_dir,
                                      custom_embeddings_dir=custom_embeddings_dir)
        
        # Step 3: Store in vector database
        logger.info("\n🗄️  Step 3: Storing in vector database...")
        collection_name = getattr(args, 'collection_name', None) or repo_name
        stats = store_repository_embeddings(base_dir, repo_name, embedded_chunks, collection_name)
        
        logger.info("✅ Pipeline complete!")
        
        if args.save:
            chunks_path = get_storage_path(base_dir, 'chunks', repo_name, custom_chunks_dir)
            embeddings_path = get_storage_path(base_dir, 'embeddings', repo_name, custom_embeddings_dir)
            logger.info("   💾 Artifacts saved in: %s and %s", chunks_path, embeddings_path)
            logger.info("   📝 Chunks: %d", len(chunks))
        logger.info("   🧠 Embeddings: %d", len(embedded_chunks))
        logger.info("   📊 Stored: %d", stats["stored_count"])
        logger.info("   📚 Collection: %s", stats["collection_name"])
        if "db_path" in stats:  # Only show when using local persistence
            logger.info("   🗄️  Database: %s", stats["db_path"])
        else:
            logger.info("   🌐 Saved in ChromaDB server")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        exit(1)


def query_func(args):
    logger.info("query this functionality")
    pass


def async_batch_func(args):
    """Process multiple repositories asynchronously."""
    import asyncio
    import json
    from .ingestion import AsyncIngestionService
    from pathlib import Path
    
    try:
        # Load repos from JSON file
        repos_file = Path(args.repos_file)
        if not repos_file.exists():
            logger.error(f"Repos file not found: {repos_file}")
            sys.exit(1)
        
        with open(repos_file, 'r') as f:
            repos = json.load(f)
        
        if not isinstance(repos, list):
            logger.error("Repos file must contain a JSON array of repo objects")
            sys.exit(1)
        
        # Validate repo format
        for i, repo in enumerate(repos):
            if 'repo_url' not in repo or 'collection_name' not in repo:
                logger.error(f"Repo {i} missing required fields: repo_url, collection_name")
                sys.exit(1)
        
        base_dir = getattr(args, 'output', None) or os.getcwd()
        max_concurrent = getattr(args, 'max_concurrent', 3)
        cleanup = not getattr(args, 'no_cleanup', False)
        
        logger.info(f"🚀 Starting async batch processing for {len(repos)} repositories")
        logger.info(f"   Base directory: {base_dir}")
        logger.info(f"   Max concurrent: {max_concurrent}")
        logger.info(f"   Cleanup: {cleanup}")
        
        # Run async batch processing
        async def run_batch():
            service = AsyncIngestionService(base_dir=base_dir)
            results = await service.process_batch_async(
                repos=repos,
                max_concurrent=max_concurrent,
                cleanup=cleanup
            )
            return results
        
        results = asyncio.run(run_batch())
        
        # Report results
        success_count = sum(1 for r in results if r.get('status') == 'success')
        failed_count = len(results) - success_count
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Batch processing complete!")
        logger.info(f"   Success: {success_count}/{len(repos)}")
        logger.info(f"   Failed: {failed_count}/{len(repos)}")
        
        # Show details for failed repos
        if failed_count > 0:
            logger.info(f"\n❌ Failed repositories:")
            for r in results:
                if r.get('status') == 'failed':
                    logger.info(f"   - {r.get('repo_url', 'unknown')}: {r.get('error', 'unknown error')}")
        
        # Save results if requested
        if hasattr(args, 'results_file') and args.results_file:
            results_path = Path(args.results_file)
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"\n💾 Results saved to: {results_path}")
        
        sys.exit(0 if failed_count == 0 else 1)
        
    except Exception as e:
        logger.error(f"Async batch processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ============================================================================
# SEARCH TOOL COMMANDS
# ============================================================================

def search_func(args):
    """Semantic search using natural language queries."""
    from .tools import semantic_search
    import asyncio
    from .utils.output_formatter import format_search_results, export_results_json, export_results_toon
    
    try:
        query = ' '.join(args.query_text) if isinstance(args.query_text, list) else args.query_text
        
        results = asyncio.run(semantic_search(
            collection_name=args.collection,
            query=query,
            n_results=args.n_results,
            language=getattr(args, 'language', None),
            include_parents=getattr(args, 'include_parents', False),
            chromadb_dir=getattr(args, 'chromadb_dir', None)
        ))

        
        result_data = {
            'query': query,
            'collection': args.collection,
            'total_results': len(results),
            'results': results
        }
        
        if args.json:
            export_results_json(result_data, args.json)
        
        if getattr(args, 'toon', None):
            export_results_toon(result_data, args.toon)
        
        if not args.json and not getattr(args, 'toon', None):
            format_search_results(results, query=query, collection=args.collection)
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        exit(1)


def symbol_func(args):
    """Find symbols (functions/classes) by name."""
    from .tools import symbol_search
    import asyncio
    from .utils.output_formatter import format_search_results, export_results_json, export_results_toon
    
    try:
        results = asyncio.run(symbol_search(
            collection_name=args.collection,
            symbol_name=args.symbol_name,
            symbol_type=getattr(args, 'type', None),
            chromadb_dir=getattr(args, 'chromadb_dir', None)
        ))
        
        result_data = {
            'symbol': args.symbol_name,
            'collection': args.collection,
            'total_results': len(results),
            'results': results
        }
        
        if args.json:
            export_results_json(result_data, args.json)
        
        if getattr(args, 'toon', None):
            export_results_toon(result_data, args.toon)
        
        if not args.json and not getattr(args, 'toon', None):
            format_search_results(results, query=f"Symbol: {args.symbol_name}", collection=args.collection)
        
    except Exception as e:
        logger.error(f"Symbol search failed: {e}")
        exit(1)


def cat_file_func(args):
    """Display complete file contents from chunks."""
    import asyncio
    from .tools import cat_file
    from .utils.output_formatter import export_results_json
    
    try:
        content = asyncio.run(cat_file(
            collection_name=args.collection,
            file_path=args.file_path,
            chromadb_dir=getattr(args, 'chromadb_dir', None)
        ))
        
        if args.json:
            export_results_json({"file_path": args.file_path, "content": content}, args.json)
        else:
            print(f"File: {args.file_path}")
            print("=" * 80)
            print(content)
        
    except Exception as e:
        logger.error(f"Cat file failed: {e}")
        exit(1)


def grep_func(args):
    """Advanced grep search with optional regex support."""
    from .tools import grep_search
    import asyncio
    from .utils.output_formatter import export_results_json
    
    try:
        results = asyncio.run(grep_search(
            collection_name=args.collection,
            pattern=args.pattern,
            max_chunks=getattr(args, 'limit', 100),
            use_regex=getattr(args, 'regex', False),
            case_sensitive=getattr(args, 'case_sensitive', False),
            whole_word=getattr(args, 'whole_word', False),
            context_lines=getattr(args, 'context', 0),
            language=getattr(args, 'language', None),
            chromadb_dir=getattr(args, 'chromadb_dir', None)
        ))
        
        if args.json:
            export_results_json(results, args.json)
        else:
            mode = "Regex" if getattr(args, 'regex', False) else "Text"
            print(f"{mode} Pattern: '{args.pattern}'")
            print(f"Found {results['total_matches']} matches in {results['total_files']} files\n")
            
            for file_result in results['files']:
                print(f"\n📄 {file_result['path']} ({file_result['match_count']} matches)")
                for match in file_result['matches'][:10]:
                    if getattr(args, 'context', 0) > 0:
                        if match.get('context_before'):
                            for ctx in match['context_before']:
                                print(f"      {ctx}")
                        print(f"  Line {match['line_number']}: {match['content']}")
                        if match.get('context_after'):
                            for ctx in match['context_after']:
                                print(f"      {ctx}")
                    else:
                        print(f"  Line {match['line_number']}: {match['content']}")
                if len(file_result['matches']) > 10:
                    print(f"  ... and {len(file_result['matches']) - 10} more matches")
        
    except Exception as e:
        logger.error(f"Grep search failed: {e}")
        exit(1)


def read_file_func(args):
    """Reconstruct and display complete file from chunks."""
    import asyncio
    from .tools import cat_file
    from .utils.output_formatter import export_results_json, export_results_toon
    
    try:
        content = asyncio.run(cat_file(
            collection_name=args.collection,
            file_path=args.file_path,
            chromadb_dir=getattr(args, 'chromadb_dir', None)
        ))
        
        file_data = {
            'file_path': args.file_path,
            'content': content
        }
        
        if args.json:
            export_results_json(file_data, args.json)
        elif getattr(args, 'toon', None):
            export_results_toon(file_data, args.toon)
        else:
            print(content)
        
    except Exception as e:
        logger.error(f"Read file failed: {e}")
        exit(1)


def search_advanced_func(args):
    """Advanced search with multiple criteria - uses grep for pattern matching."""
    from .tools import semantic_search, grep_search
    from .utils.output_formatter import format_search_results, export_results_json, export_results_toon
    
    try:
        # Use semantic search if query provided
        if args.semantic:
            results = asyncio.run(semantic_search(
                collection_name=args.collection,
                query=args.semantic,
                n_results=args.limit,
                language=args.language if hasattr(args, 'language') else None,
                chromadb_dir=getattr(args, 'chromadb_dir', None)
            ))
            query_desc = f"Semantic: {args.semantic}"
            
            result_data = {
                'query': query_desc,
                'collection': args.collection,
                'total_results': len(results),
                'results': results
            }
            
            if args.json:
                export_results_json(result_data, args.json)
            elif getattr(args, 'toon', None):
                export_results_toon(result_data, args.toon)
            else:
                format_search_results(results, query=query_desc, collection=args.collection)
                
        elif args.pattern:
            # Use grep search for pattern
            results = asyncio.run(grep_search(
                collection_name=args.collection,
                pattern=args.pattern,
                max_chunks=args.limit,
                chromadb_dir=getattr(args, 'chromadb_dir', None)
            ))
            
            if args.json:
                export_results_json(results, args.json)
            else:
                print(f"Pattern: '{args.pattern}'")
                print(f"Found {results['total_matches']} matches in {results['total_files']} files")
        else:
            logger.error("Please provide either --semantic or --pattern")
            exit(1)
        
    except Exception as e:
        logger.error(f"Advanced search failed: {e}")
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
        custom_chromadb_dir = getattr(args, 'chromadb_dir', None)
        vector_store = ChromaVectorStore(base_dir=base_dir, repo_name=repo_name, custom_chromadb_dir=custom_chromadb_dir)
        collections = vector_store.list_collections()
        
        logger.info("ChromaDB Database Information")
        logger.info(f"Database path: {vector_store.db_path}")
        logger.info("=" * 50)
        
        if not collections:
            logger.info("📭 No collections found in the database")
            return
        
        logger.info(f"Found {len(collections)} collection(s):")
        logger.info("")
        
        for collection in collections:
            logger.info("  📖 Collection: %s", collection["name"])
            logger.info("     📊 Documents: %d", collection["count"])
            if collection.get('metadata'):
                logger.info("     📝 Description: %s", collection["metadata"].get("description", "N/A"))
            logger.info("")
        
        # Show total documents
        total_docs = sum(col['count'] for col in collections)
        logger.info(f"Total documents across all collections: {total_docs}")
        
    except Exception as e:
        logger.error(f"Failed to get database info: {str(e)}")
        exit(1)


def db_list_func(args):
    """List all collections in ChromaDB."""
    from .vectorstore import ChromaVectorStore
    import os
    from pathlib import Path
    
    try:
        # Use output directory if provided, otherwise current directory
        base_dir = getattr(args, 'output', None) or os.getcwd()
        custom_chromadb_dir = getattr(args, 'chromadb_dir', None)
        repo_name = getattr(args, 'repo_name', None) or Path(base_dir).name
        
        vector_store = ChromaVectorStore(base_dir=base_dir, repo_name=repo_name, custom_chromadb_dir=custom_chromadb_dir)
        collections = vector_store.list_collections()
        
        logger.info(f"Database path: {vector_store.db_path}")
        
        if not collections:
            logger.info("📭 No collections found")
            return
        
        logger.info("📚 Collections:")
        for collection in collections:
            logger.info("  - %s (%d documents)", collection["name"], collection["count"])
        
    except Exception as e:
        logger.error(f"Failed to list collections: {str(e)}")
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
        custom_chromadb_dir = getattr(args, 'chromadb_dir', None)
        repo_name = getattr(args, 'repo_name', None) or Path(base_dir).name
        
        collection_name = args.collection_name
        vector_store = ChromaVectorStore(base_dir=base_dir, repo_name=repo_name, custom_chromadb_dir=custom_chromadb_dir)
        
        logger.info(f"Database path: {vector_store.db_path}")
        
        # Get collection info
        info = vector_store.get_collection_info(collection_name)
        
        if not info.get('exists', True):
            logger.error(f"Collection '{collection_name}' not found")
            return
        
        logger.info(f"Collection: {info['name']}")
        logger.info(f"Documents: {info['count']}")
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
        custom_chromadb_dir = getattr(args, 'chromadb_dir', None)
        repo_name = getattr(args, 'repo_name', None) or Path(base_dir).name
        
        collection_name = args.collection_name
        vector_store = ChromaVectorStore(base_dir=base_dir, repo_name=repo_name, custom_chromadb_dir=custom_chromadb_dir)
        
        logger.info(f"Database path: {vector_store.db_path}")
        
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
            logger.info(f"✅ Collection '{collection_name}' deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            exit(1)
        
    except Exception as e:
        logger.error(f"Failed to clear collection: {str(e)}")
        exit(1)


def main():
    # Check if no arguments or just --help/-h is provided
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h', 'help']):
        print_main_help()
        sys.exit(0)
    
    parser = argparse.ArgumentParser(
        prog='contextinator',
        description='Contextinator — Turn any codebase into semantically-aware, searchable knowledge for AI',
        add_help=False,  # We handle help ourselves
        epilog='Examples:\n'
            '  %(prog)s chunk --repo-url https://github.com/user/repo --save\n'
            '  %(prog)s search "authentication logic" -c MyRepo -n 5\n'
            '  %(prog)s search-advanced -c MyRepo --semantic "error handling" --language python\n\n'
            'For detailed help on a command: %(prog)s <command> --help',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add custom help argument
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message')
    
    sub = parser.add_subparsers(title='commands', dest='command')

    # chunk
    p_chunk = sub.add_parser('chunk', help='Chunks the local Git codebase into semantic units and (optionally) save them', formatter_class=RichHelpFormatter)
    p_chunk.add_argument('--save', action='store_true', help='Save chunks to .contextinator/chunks/ folder')
    p_chunk.add_argument('--save-ast', action='store_true', help='Save AST trees for analysis and debugging')
    p_chunk.add_argument('--repo-url', help='GitHub/Git repository URL to clone and chunk')
    p_chunk.add_argument('--path', help='Local path to repository (default: current directory)')
    p_chunk.add_argument('--output', '-o', help='Output directory for chunks (default: current directory)')
    p_chunk.add_argument('--chunks-dir', help='Custom chunks directory (overrides default .contextinator/chunks)')
    p_chunk.set_defaults(func=chunk_func)

    # embed
    p_embed = sub.add_parser('embed', help='Generate embeddings for existing chunks using OpenAI and (optionally) save them', formatter_class=RichHelpFormatter)
    p_embed.add_argument('--save', action='store_true', help='Save embeddings to .contextinator/embeddings/ folder')
    p_embed.add_argument('--repo-url', help='GitHub/Git repository URL to clone and embed')
    p_embed.add_argument('--path', help='Local path to repository (default: current directory)')
    p_embed.add_argument('--output', '-o', help='Base directory containing chunks folder (default: current directory)')
    p_embed.add_argument('--chunks-dir', help='Custom chunks directory (overrides default .contextinator/chunks)')
    p_embed.add_argument('--embeddings-dir', help='Custom embeddings directory (overrides default .contextinator/embeddings)')
    p_embed.add_argument('--api-key', help='OpenAI API key (alternative to OPENAI_API_KEY env var)')  
    p_embed.set_defaults(func=embed_func)

    # store-embeddings
    p_store = sub.add_parser('store-embeddings', help='Load embeddings into ChromaDB vector store', formatter_class=RichHelpFormatter)
    p_store.add_argument('--repo-url', help='GitHub/Git repository URL')
    p_store.add_argument('--path', help='Local path to repository (default: current directory)')
    p_store.add_argument('--output', '-o', help='Base directory containing embeddings folder (default: current directory)')
    p_store.add_argument('--embeddings-dir', help='Custom embeddings directory (overrides default .contextinator/embeddings)')
    p_store.add_argument('--chromadb-dir', help='Custom chromadb directory (overrides default .contextinator/chromadb)')
    p_store.add_argument('--repo-name', help='Repository name (for locating embeddings when not using --repo-url or --path)')
    p_store.add_argument('--collection-name', help='Custom collection name (default: repository name)')
    p_store.set_defaults(func=store_embeddings_func)

    # combined pipeline: chunk-embed-store-embeddings
    p_pipeline = sub.add_parser('chunk-embed-store-embeddings', help='Run chunk, embed and store-embeddings in a single command', formatter_class=RichHelpFormatter)
    p_pipeline.add_argument('--save', action='store_true', help='Save intermediate artifacts (chunks + embeddings)')
    p_pipeline.add_argument('--repo-url', help='GitHub/Git repository URL to clone and process')
    p_pipeline.add_argument('--path', help='Local path to repository (default: current directory)')
    p_pipeline.add_argument('--output', '-o', help='Base output directory (default: current directory)')
    p_pipeline.add_argument('--chunks-dir', help='Custom chunks directory (overrides default .contextinator/chunks)')
    p_pipeline.add_argument('--embeddings-dir', help='Custom embeddings directory (overrides default .contextinator/embeddings)')
    p_pipeline.add_argument('--chromadb-dir', help='Custom chromadb directory (overrides default .contextinator/chromadb)')
    p_pipeline.add_argument('--collection-name', help='Custom collection name (default: repository name)')
    p_pipeline.add_argument('--api-key', help='OpenAI API key (alternative to OPENAI_API_KEY env var)')   
    p_pipeline.set_defaults(func=pipeline_func)

    # query
    p_query = sub.add_parser('query', help='Query the vector store for semantically similar code chunks', formatter_class=RichHelpFormatter)
    p_query.add_argument('query_text', nargs=argparse.REMAINDER, help='Query text (wrap in quotes if multiple words)')
    p_query.add_argument('--n-results', '-n', type=int, default=5, help='Number of results to return')
    p_query.add_argument('--save', metavar='FILE', help='Save results to a file (JSON or text)')
    p_query.set_defaults(func=query_func)

    # db-info
    p_db_info = sub.add_parser('db-info', help='Show ChromaDB database information and statistics', formatter_class=RichHelpFormatter)
    p_db_info.add_argument('--repo-name', help='Repository name (for locating database when not using --output)')
    p_db_info.add_argument('--chromadb-dir', help='Custom chromadb directory (overrides default .contextinator/chromadb)')
    p_db_info.set_defaults(func=db_info_func)

    # db-list
    p_db_list = sub.add_parser('db-list', help='List all collections in ChromaDB', formatter_class=RichHelpFormatter)
    p_db_list.add_argument('--repo-name', help='Repository name (for locating database when not using --output)')
    p_db_list.add_argument('--chromadb-dir', help='Custom chromadb directory (overrides default .contextinator/chromadb)')
    p_db_list.set_defaults(func=db_list_func)

    # db-show
    p_db_show = sub.add_parser('db-show', help='Show details of a specific collection', formatter_class=RichHelpFormatter)
    p_db_show.add_argument('collection_name', help='Name of the collection to show')
    p_db_show.add_argument('--sample', type=int, default=0, help='Show sample documents (specify number)')
    p_db_show.add_argument('--repo-name', help='Repository name (for locating database when not using --output)')
    p_db_show.add_argument('--chromadb-dir', help='Custom chromadb directory (overrides default .contextinator/chromadb)')
    p_db_show.set_defaults(func=db_show_func)

    # db-clear
    p_db_clear = sub.add_parser('db-clear', help='Delete a specific collection', formatter_class=RichHelpFormatter)
    p_db_clear.add_argument('collection_name', help='Name of the collection to delete')
    p_db_clear.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    p_db_clear.set_defaults(func=db_clear_func)

    p_db_clear.add_argument('--repo-name', help='Repository name (for locating database when not using --output)')
    p_db_clear.add_argument('--chromadb-dir', help='Custom chromadb directory (overrides default .contextinator/chromadb)')

    # structure
    p_structure = sub.add_parser('structure', help='Analyze and display repository structure as a tree', formatter_class=RichHelpFormatter)
    p_structure.add_argument('--repo-url', help='GitHub/Git repository URL to analyze')
    p_structure.add_argument('--path', help='Local path to repository (default: current directory)')
    p_structure.add_argument('--depth', type=int, help='Maximum depth to traverse (default: unlimited)')
    p_structure.add_argument('--format', choices=['tree', 'json'], default='tree', help='Output format (default: tree)')
    p_structure.add_argument('--output', '-o', help='Save output to file')
    p_structure.set_defaults(func=structure_func)

    # ========================================================================
    # SEARCH TOOL COMMANDS
    # ========================================================================

    # search (semantic search)
    p_search = sub.add_parser(
        'search',
        help='Semantic search using natural language queries',
        description='Search for code using natural language. By default, excludes parent chunks (classes/modules) for cleaner results.',
        epilog='Examples:\n'
            '  %(prog)s "authentication logic" -c MyRepo\n'
            '  %(prog)s "error handling" -c MyRepo --language python -n 10\n'
            '  %(prog)s "database queries" -c MyRepo --include-parents\n'
            '  %(prog)s "API endpoints" -c MyRepo --toon results.json',
        formatter_class=RichHelpFormatter
    )
    p_search.add_argument('query_text', nargs='+', help='Natural language query')
    p_search.add_argument('--collection', '-c', required=True, help='Collection name')
    p_search.add_argument('--n-results', '-n', type=int, default=5, help='Number of results (default: 5)')
    p_search.add_argument('--language', '-l', help='Filter by programming language')
    p_search.add_argument('--file', '-f', help='Filter by file path (partial match)')
    p_search.add_argument('--type', '-t', help='Filter by node type')
    p_search.add_argument('--include-parents', action='store_true', help='Include parent chunks (classes/modules) in results')
    p_search.add_argument('--json', help='Export results to JSON file')
    p_search.add_argument('--toon', help='Export results to TOON file (compact format)')
    p_search.add_argument('--chromadb-dir', help='Custom chromadb directory (overrides default .contextinator/chromadb)')
    p_search.set_defaults(func=search_func)

    # symbol (symbol search)
    p_symbol = sub.add_parser(
        'symbol',
        help='Find symbols (functions/classes) by exact or partial name match',
        description='Search for specific function or class names across the codebase.',
        epilog='Examples:\n'
            '  %(prog)s authenticate_user -c MyRepo\n'
            '  %(prog)s UserManager -c MyRepo --type class_definition\n'
            '  %(prog)s "get_*" -c MyRepo --file "api/"\n'
            '  %(prog)s main -c MyRepo --json results.json',
        formatter_class=RichHelpFormatter
    )
    p_symbol.add_argument('symbol_name', help='Symbol name to search for')
    p_symbol.add_argument('--collection', '-c', required=True, help='Collection name')
    p_symbol.add_argument('--type', '-t', help='Filter by node type')
    p_symbol.add_argument('--file', '-f', help='Filter by file path (partial match)')
    p_symbol.add_argument('--limit', type=int, default=50, help='Maximum results (default: 50)')
    p_symbol.add_argument('--json', help='Export results to JSON file')
    p_symbol.add_argument('--toon', help='Export results to TOON file (compact format)')
    p_symbol.add_argument('--chromadb-dir', help='Custom chromadb directory (overrides default .contextinator/chromadb)')
    p_symbol.set_defaults(func=symbol_func)

    # pattern (regex search)
    p_cat = sub.add_parser('cat', help='Display complete file contents from chunks', formatter_class=RichHelpFormatter)
    p_cat.add_argument('file_path', help='File path to display')
    p_cat.add_argument('--collection', '-c', required=True, help='Collection name')
    p_cat.add_argument('--json', help='Export to JSON file')
    p_cat.add_argument('--chromadb-dir', help='Custom chromadb directory')
    p_cat.set_defaults(func=cat_file_func)

    # grep (advanced search with $contains)
    p_grep = sub.add_parser('grep', help='Advanced grep search with optional regex support', formatter_class=RichHelpFormatter)
    p_grep.add_argument('pattern', help='Text pattern or regex to search for')
    p_grep.add_argument('--collection', '-c', required=True, help='Collection name')
    p_grep.add_argument('--limit', type=int, default=100, help='Maximum chunks to search (default: 100)')
    p_grep.add_argument('--regex', action='store_true', help='Enable regex pattern matching')
    p_grep.add_argument('--case-sensitive', action='store_true', help='Case-sensitive matching')
    p_grep.add_argument('--whole-word', action='store_true', help='Match whole words only')
    p_grep.add_argument('--context', type=int, default=0, help='Number of context lines before/after match')
    p_grep.add_argument('--language', '-l', help='Filter by programming language')
    p_grep.add_argument('--json', help='Export to JSON file')
    p_grep.add_argument('--chromadb-dir', help='Custom chromadb directory')
    p_grep.set_defaults(func=grep_func)

    # read-file (file reconstruction)
    p_read_file = sub.add_parser('read-file', help='Reconstruct and display complete file from chunks', formatter_class=RichHelpFormatter)
    p_read_file.add_argument('file_path', help='File path to read')
    p_read_file.add_argument('--collection', '-c', required=True, help='Collection name')
    p_read_file.add_argument('--no-join', action='store_true', help='Show chunks separately (don\'t join)')
    p_read_file.add_argument('--json', help='Export to JSON file')
    p_read_file.add_argument('--toon', help='Export to TOON file (compact format)')
    p_read_file.add_argument('--chromadb-dir', help='Custom chromadb directory (overrides default .contextinator/chromadb)')
    p_read_file.set_defaults(func=read_file_func)

    # search-advanced (advanced/hybrid search)
    p_search_adv = sub.add_parser(
        'search-advanced',
        help='Advanced search with multiple criteria and filters',
        description='Combine semantic search, pattern matching, and metadata filters for precise results.',
        epilog='Examples:\n'
            '  # Semantic search with language filter\n'
            '  %(prog)s -c MyRepo --semantic "authentication" --language python\n\n'
            '  # Pattern search with file filter\n'
            '  %(prog)s -c MyRepo --pattern "TODO" --file "src/"\n\n'
            '  # Hybrid: semantic + pattern + type filter\n'
            '  %(prog)s -c MyRepo --semantic "error handling" --pattern "try" --type function_definition\n\n'
            '  # Export to TOON format\n'
            '  %(prog)s -c MyRepo --semantic "API routes" --toon api_routes.json',
        formatter_class=RichHelpFormatter
    )
    p_search_adv.add_argument('--collection', '-c', required=True, help='Collection name')
    p_search_adv.add_argument('--semantic', '-s', help='Semantic query for hybrid search')
    p_search_adv.add_argument('--pattern', '-p', help='Text pattern to search for')
    p_search_adv.add_argument('--language', '-l', help='Filter by programming language')
    p_search_adv.add_argument('--file', '-f', help='Filter by file path (partial match)')
    p_search_adv.add_argument('--type', '-t', help='Filter by node type')
    p_search_adv.add_argument('--limit', type=int, default=50, help='Maximum results (default: 50)')
    p_search_adv.add_argument('--json', help='Export results to JSON file')
    p_search_adv.add_argument('--toon', help='Export results to TOON file (compact format)')
    p_search_adv.add_argument('--chromadb-dir', help='Custom chromadb directory (overrides default .contextinator/chromadb)')
    p_search_adv.set_defaults(func=search_advanced_func)

    # async-batch (async batch processing)
    p_async_batch = sub.add_parser(
        'async-batch',
        help='Process multiple repositories asynchronously',
        description='Batch process multiple repositories concurrently using async pipeline.',
        epilog='Examples:\n'
            '  # Process repos from JSON file\n'
            '  %(prog)s repos.json --max-concurrent 3\n\n'
            '  # With custom output directory\n'
            '  %(prog)s repos.json --output ./data --max-concurrent 5\n\n'
            '  # Save results to file\n'
            '  %(prog)s repos.json --results results.json\n\n'
            'JSON format:\n'
            '  [\n'
            '    {"repo_url": "https://github.com/user/repo1", "collection_name": "repo1"},\n'
            '    {"repo_url": "https://github.com/user/repo2", "collection_name": "repo2"}\n'
            '  ]',
        formatter_class=RichHelpFormatter
    )
    p_async_batch.add_argument('repos_file', help='JSON file containing list of repositories')
    p_async_batch.add_argument('--output', '-o', help='Base output directory (default: current directory)')
    p_async_batch.add_argument('--max-concurrent', type=int, default=3, help='Max concurrent repositories (default: 3)')
    p_async_batch.add_argument('--no-cleanup', action='store_true', help='Keep temporary cloned directories')
    p_async_batch.add_argument('--results', dest='results_file', help='Save results to JSON file')
    p_async_batch.set_defaults(func=async_batch_func)

    args = parser.parse_args()

    # Handle help flag
    if hasattr(args, 'help') and args.help and not args.command:
        print_main_help()
        sys.exit(0)

    # If no subcommand was provided, show help and exit
    if not hasattr(args, 'func'):
        print_main_help()
        sys.exit(1)

    # Call the selected subcommand handler
    args.func(args)


if __name__ == '__main__':
    main()
