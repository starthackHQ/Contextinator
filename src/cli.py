import argparse
import sys
from .utils import resolve_repo_path


def chunk_func(args):
    from .chunk import chunk_repository
    import os
    
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
    print("embed this functionality")
    pass


def store_embeddings_func(args):
    print("store-embeddings this functionality")
    pass


def pipeline_func(args):
    # combined chunk + embed + store-embeddings
    print("chunk-embed-store-embeddings this functionality")
    pass


def query_func(args):
    print("query this functionality")
    pass


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
    p_embed = sub.add_parser('embed', help='Generate embeddings for existing chunks and (optionally) save them')
    p_embed.add_argument('--save', action='store_true', help='Save embeddings to a .embeddings folder')
    p_embed.add_argument('--model-name-or-path', '-m', default='krlvi/sentence-msmarco-bert-base-dot-v5-nlpl-code_search_net',
                         help='Model name or path to use for embeddings (placeholder)')
    p_embed.add_argument('--batch-size', '-b', type=int, default=32, help='Batch size for embeddings generation')
    p_embed.set_defaults(func=embed_func)

    # store-embeddings
    p_store = sub.add_parser('store-embeddings', help='Load embeddings into a vector store (e.g., Chroma)')
    p_store.add_argument('--vectorstore', choices=['chroma'], default='chroma', help='Vector store backend to use')
    p_store.add_argument('--db-path', default='.chroma_db', help='Local path where the vector DB will be stored')
    p_store.set_defaults(func=store_embeddings_func)

    # combined pipeline: chunk-embed-store-embeddings
    p_pipeline = sub.add_parser('chunk-embed-store-embeddings', help='Run chunk, embed and store-embeddings in a single command')
    p_pipeline.add_argument('--save', action='store_true', help='Save intermediate artifacts (chunks + embeddings)')
    p_pipeline.add_argument('--vectorstore', choices=['chroma'], default='chroma', help='Vector store backend to use')
    p_pipeline.add_argument('--db-path', default='.chroma_db', help='Local path for the vector DB')
    p_pipeline.set_defaults(func=pipeline_func)

    # query
    p_query = sub.add_parser('query', help='Query the vector store for semantically similar code chunks')
    p_query.add_argument('query_text', nargs=argparse.REMAINDER, help='Query text (wrap in quotes if multiple words)')
    p_query.add_argument('--n-results', '-n', type=int, default=5, help='Number of results to return')
    p_query.add_argument('--save', metavar='FILE', help='Save results to a file (JSON or text)')
    p_query.set_defaults(func=query_func)

    args = parser.parse_args()

    # If no subcommand was provided, show help and exit
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    # Call the selected subcommand handler
    args.func(args)


if __name__ == '__main__':
    main()
