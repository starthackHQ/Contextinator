"""
Contextinator v2.0 CLI

Primary commands: fs_read tools
Secondary commands: rag module (v1 functionality)
"""

import argparse
import json
import sys
from pathlib import Path


def read_command(args):
    """Execute fs_read tool."""
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


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="contextinator",
        description="Filesystem tools for AI agents"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Read command
    read_parser = subparsers.add_parser("read", help="Read filesystem")
    read_parser.add_argument("--path", required=True, help="File or directory path")
    read_parser.add_argument(
        "--mode",
        required=True,
        choices=["Line", "Directory", "Search"],
        help="Operation mode"
    )
    read_parser.add_argument("--start-line", type=int, help="Start line (Line mode)")
    read_parser.add_argument("--end-line", type=int, help="End line (Line mode)")
    read_parser.add_argument("--depth", type=int, default=0, help="Depth (Directory mode)")
    read_parser.add_argument("--pattern", help="Search pattern (Search mode)")
    read_parser.add_argument("--context-lines", type=int, default=2, help="Context lines (Search mode)")
    read_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    read_parser.set_defaults(func=read_command)
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version")
    version_parser.set_defaults(func=lambda args: print("contextinator v2.0.0"))
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
