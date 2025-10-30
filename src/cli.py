import argparse
import sys
from .utils import resolve_repo_path
import os    
from .chunking import chunk_repository

def chunk_func(args):
    repo_path = resolve_repo_path(
        repo_url=getattr(args, 'repo_url', None),
        path=getattr(args, 'path', None)
    )
    
    # Use output dir if specified, otherwise current directory
    output_dir = getattr(args, 'output', None) or os.getcwd()
    
    # Check if AST saving is requested
    save_ast = getattr(args, 'save_ast', False)
    
    chunks = chunk_repository(
        repo_path, 
        save=args.save, 
        output_dir=output_dir, 
        save_ast=save_ast
    )
    print(f"\n✅ Chunking complete: {len(chunks)} chunks created")
    
    if save_ast:
        print(f"🌳 AST trees saved for analysis")
        print(f"📁 Check: {output_dir}/.chunks/ast_trees/ for AST files")


def embed_func(args):
    """Generate embeddings for existing chunks."""
    from .embedding import embed_chunks
    from .utils import resolve_repo_path
    import os
    
    try:
        repo_path = resolve_repo_path(
            repo_url=getattr(args, 'repo_url', None),
            path=getattr(args, 'path', None)
        )
        
        print(f"🚀 Generating embeddings for repository: {repo_path}")
        
        # Generate embeddings
        embedded_chunks = embed_chunks(repo_path, save=args.save)
        
        print(f"✅ Embedding generation complete: {len(embedded_chunks)} chunks embedded")
        
        if args.save:
            print(f"💾 Embeddings saved to {repo_path}/.embeddings/")
        
    except Exception as e:
        print(f"❌ Embedding generation failed: {str(e)}")
        exit(1)


def store_embeddings_func(args):
    """Store embeddings in ChromaDB vector store."""
    from .embedding import load_embeddings
    from .vectorstore import store_repository_embeddings
    from .utils import resolve_repo_path
    from pathlib import Path
    
    try:
        repo_path = resolve_repo_path(
            repo_url=getattr(args, 'repo_url', None),
            path=getattr(args, 'path', None)
        )
        
        print(f"🗄️  Storing embeddings for repository: {repo_path}")
        
        # Load embeddings
        embedded_chunks = load_embeddings(repo_path)
        
        # Determine collection name
        collection_name = getattr(args, 'collection_name', None) or Path(repo_path).name
        
        # Store in ChromaDB
        stats = store_repository_embeddings(repo_path, embedded_chunks, collection_name)
        
        print(f"✅ Storage complete:")
        print(f"   📊 Stored: {stats['stored_count']} embeddings")
        print(f"   📚 Collection: {stats['collection_name']}")
        print(f"   🗄️  Database: {stats['db_path']}")
        
    except Exception as e:
        print(f"❌ Embedding storage failed: {str(e)}")
        exit(1)


def pipeline_func(args):
    """Combined chunk + embed + store-embeddings pipeline."""
    from .embedding import embed_chunks
    from .vectorstore import store_repository_embeddings
    from .utils import resolve_repo_path
    from pathlib import Path
    import os
    
    try:
        repo_path = resolve_repo_path(
            repo_url=getattr(args, 'repo_url', None),
            path=getattr(args, 'path', None)
        )
        
        print(f"🚀 Starting complete pipeline for repository: {repo_path}")
        
        # Step 1: Chunk repository
        print("\n📝 Step 1: Chunking repository...")
        chunks = chunk_repository(repo_path, save=args.save)
        
        if not chunks:
            print("❌ No chunks generated. Pipeline stopped.")
            exit(1)
        
        # Step 2: Generate embeddings
        print("\n🧠 Step 2: Generating embeddings...")
        embedded_chunks = embed_chunks(repo_path, save=args.save, chunks_data=chunks)
        
        # Step 3: Store in vector database
        print("\n🗄️  Step 3: Storing in vector database...")
        collection_name = getattr(args, 'collection_name', None) or Path(repo_path).name
        stats = store_repository_embeddings(repo_path, embedded_chunks, collection_name)
        
        print(f"\n✅ Pipeline complete!")
        print(f"   📝 Chunks: {len(chunks)}")
        print(f"   🧠 Embeddings: {len(embedded_chunks)}")
        print(f"   📊 Stored: {stats['stored_count']}")
        print(f"   📚 Collection: {stats['collection_name']}")
        print(f"   🗄️  Database: {stats['db_path']}")
        
        if args.save:
            print(f"   💾 Artifacts saved in: {repo_path}")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
        exit(1)


def query_func(args):
    print("query this functionality")
    pass


def db_info_func(args):
    """Show ChromaDB database information."""
    from .vectorstore import ChromaVectorStore
    
    try:
        vector_store = ChromaVectorStore()
        collections = vector_store.list_collections()
        
        print(f"🗄️  ChromaDB Database Information")
        print(f"=" * 50)
        
        if not collections:
            print("📭 No collections found in the database")
            return
        
        print(f"📚 Found {len(collections)} collection(s):")
        print()
        
        for collection in collections:
            print(f"  📖 Collection: {collection['name']}")
            print(f"     📊 Documents: {collection['count']}")
            if collection.get('metadata'):
                print(f"     📝 Description: {collection['metadata'].get('description', 'N/A')}")
            print()
        
        # Show total documents
        total_docs = sum(col['count'] for col in collections)
        print(f"📈 Total documents across all collections: {total_docs}")
        
    except Exception as e:
        print(f"❌ Failed to get database info: {str(e)}")
        exit(1)


def db_list_func(args):
    """List all collections in ChromaDB."""
    from .vectorstore import ChromaVectorStore
    
    try:
        vector_store = ChromaVectorStore()
        collections = vector_store.list_collections()
        
        if not collections:
            print("📭 No collections found")
            return
        
        print("📚 Collections:")
        for collection in collections:
            print(f"  - {collection['name']} ({collection['count']} documents)")
        
    except Exception as e:
        print(f"❌ Failed to list collections: {str(e)}")
        exit(1)


def db_show_func(args):
    """Show details of a specific collection."""
    from .vectorstore import ChromaVectorStore
    from .config import sanitize_collection_name
    
    try:
        collection_name = args.collection_name
        vector_store = ChromaVectorStore()
        
        # Get collection info
        info = vector_store.get_collection_info(collection_name)
        
        if not info.get('exists', True):
            print(f"❌ Collection '{collection_name}' not found")
            return
        
        print(f"📖 Collection: {info['name']}")
        print(f"📊 Documents: {info['count']}")
        if info.get('metadata'):
            print(f"📝 Description: {info['metadata'].get('description', 'N/A')}")
        
        # Get a few sample documents if requested
        if args.sample and info['count'] > 0:
            try:
                safe_name = sanitize_collection_name(collection_name)
                collection = vector_store.client.get_collection(name=safe_name)
                
                # Get first few documents
                sample_size = min(args.sample, info['count'])
                results = collection.get(limit=sample_size)
                
                print(f"\n📄 Sample documents (showing {sample_size}):")
                for i, (doc_id, document, metadata) in enumerate(zip(
                    results['ids'], results['documents'], results['metadatas']
                )):
                    print(f"\n  Document {i+1}:")
                    print(f"    ID: {doc_id}")
                    print(f"    Content: {document[:200]}{'...' if len(document) > 200 else ''}")
                    if metadata:
                        print(f"    Metadata: {metadata}")
                        
            except Exception as e:
                print(f"⚠️  Could not fetch sample documents: {str(e)}")
        
    except Exception as e:
        print(f"❌ Failed to show collection: {str(e)}")
        exit(1)


def db_clear_func(args):
    """Clear/delete a specific collection."""
    from .vectorstore import ChromaVectorStore
    from .config import sanitize_collection_name
    
    try:
        collection_name = args.collection_name
        vector_store = ChromaVectorStore()
        
        # Confirm deletion
        if not args.force:
            response = input(f"⚠️  Are you sure you want to delete collection '{collection_name}'? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled")
                return
        
        # Delete collection
        safe_name = sanitize_collection_name(collection_name)
        try:
            vector_store.client.delete_collection(name=safe_name)
            print(f"✅ Collection '{collection_name}' deleted successfully")
        except Exception as e:
            print(f"❌ Failed to delete collection: {str(e)}")
            exit(1)
        
    except Exception as e:
        print(f"❌ Failed to clear collection: {str(e)}")
        exit(1)


def main():
    parser = argparse.ArgumentParser(prog='semanticsage', description='Semanticsage — semantic codebase tooling')

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
    p_embed.set_defaults(func=embed_func)

    # store-embeddings
    p_store = sub.add_parser('store-embeddings', help='Load embeddings into ChromaDB vector store')
    p_store.add_argument('--repo-url', help='GitHub/Git repository URL')
    p_store.add_argument('--path', help='Local path to repository (default: current directory)')
    p_store.add_argument('--collection-name', help='Custom collection name (default: repository name)')
    p_store.set_defaults(func=store_embeddings_func)

    # combined pipeline: chunk-embed-store-embeddings
    p_pipeline = sub.add_parser('chunk-embed-store-embeddings', help='Run chunk, embed and store-embeddings in a single command')
    p_pipeline.add_argument('--save', action='store_true', help='Save intermediate artifacts (chunks + embeddings)')
    p_pipeline.add_argument('--repo-url', help='GitHub/Git repository URL to clone and process')
    p_pipeline.add_argument('--path', help='Local path to repository (default: current directory)')
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

    args = parser.parse_args()

    # If no subcommand was provided, show help and exit
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    # Call the selected subcommand handler
    args.func(args)


if __name__ == '__main__':
    main()
