"""
Contextinator v2.0 CLI - Rust-Powered Filesystem Tools for AI Agents

Primary interface: Rust-based fs_read tools (read command)
Optional RAG features: Available via --rag flag (requires 'pip install contextinator[rag]')
"""

import argparse
import json
import sys
from pathlib import Path


def read_command(args):
    """Execute fs_read tool (Rust-based)."""
    from contextinator import fs_read
    
    try:
        result = fs_read(
            path=args.path,
            mode=args.mode,
            start_line=args.start_line,
            end_line=args.end_line,
            depth=args.depth,
            pattern=args.pattern,
            context_lines=args.context_lines,
        )
        
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            _print_result(result, args.mode)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _print_result(result, mode):
    """Pretty print result based on mode."""
    if mode == "Line":
        print(result["content"])
        print(f"\n[{result['lines_returned']}/{result['total_lines']} lines]", file=sys.stderr)
    
    elif mode == "Directory":
        for entry in result["entries"]:
            prefix = "📁" if entry["is_dir"] else "📄"
            size = f"({entry['size']} bytes)" if not entry["is_dir"] else ""
            print(f"{prefix} {entry['path']} {size}")
        print(f"\n[{result['total_count']} entries]", file=sys.stderr)
    
    elif mode == "Search":
        for match in result["matches"]:
            print(f"\n{match['file_path']}:{match['line_number']}")
            
            for line in match["context_before"]:
                print(f"  {line}")
            
            print(f"> {match['line_content']}")
            
            for line in match["context_after"]:
                print(f"  {line}")
        
        print(f"\n[{result['total_matches']} matches]", file=sys.stderr)


def rag_command(args):
    """Execute RAG commands (requires RAG dependencies)."""
    try:
        from contextinator.rag_cli import main as rag_main
        # Reconstruct args for rag_cli
        sys.argv = [sys.argv[0]] + args.rag_args
        rag_main()
    except ImportError:
        print(
            "Error: RAG features require additional dependencies.\n"
            "Install with: pip install contextinator[rag]",
            file=sys.stderr
        )
        sys.exit(1)


def main():
    """Main CLI entry point - Rust-based tools at the forefront."""
    parser = argparse.ArgumentParser(
        prog="contextinator",
        description="Rust-powered filesystem tools for AI agents | Optional: RAG capabilities with --rag flag",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rust-based filesystem operations (v2 - default)
  contextinator read --path file.py --mode Line --start-line 1 --end-line 50
  contextinator read --path src/ --mode Directory --depth 2
  contextinator read --path . --mode Search --pattern "TODO"
  
  # RAG features (v1 - optional, requires 'rag' extras)
  contextinator --rag chunk --path ./myrepo --save
  contextinator --rag search "authentication logic" --collection MyRepo
  
For detailed documentation: https://github.com/starthackHQ/Contextinator
        """
    )
    
    # Global flag for RAG mode
    parser.add_argument(
        "--rag",
        action="store_true",
        help="Use RAG features (requires 'pip install contextinator[rag]')"
    )
    
    # Parse known args to check for --rag flag
    args, remaining = parser.parse_known_args()
    
    if args.rag:
        # Pass control to RAG CLI
        rag_args_obj = argparse.Namespace(rag_args=remaining)
        rag_command(rag_args_obj)
        return
    
    # Main v2 commands (Rust-based)
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Read command (v2 primary - Rust-based)
    read_parser = subparsers.add_parser(
        "read",
        help="Read files/directories or search patterns (Rust-based, fast)",
        description="Rust-powered filesystem operations for AI agents"
    )
    read_parser.add_argument("--path", required=True, help="File or directory path")
    read_parser.add_argument(
        "--mode",
        required=True,
        choices=["Line", "Directory", "Search"],
        help="Operation mode: Line (read file), Directory (list files), Search (pattern matching)"
    )
    read_parser.add_argument("--start-line", type=int, help="Start line number (Line mode)")
    read_parser.add_argument("--end-line", type=int, help="End line number (Line mode)")
    read_parser.add_argument("--depth", type=int, default=0, help="Directory traversal depth, 0=non-recursive (Directory mode)")
    read_parser.add_argument("--pattern", help="Search pattern/regex (Search mode)")
    read_parser.add_argument("--context-lines", type=int, default=2, help="Context lines around matches (Search mode)")
    read_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    read_parser.set_defaults(func=read_command)
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    version_parser.set_defaults(func=lambda args: print("Contextinator v2.0.2 (Rust-powered)"))
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == "__main__":
    main()
