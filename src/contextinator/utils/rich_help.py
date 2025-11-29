"""
Custom help formatter using Rich library for better CLI output.
"""
import argparse
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()


class RichHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom formatter that uses Rich for better command help output."""
    
    def format_help(self):
        """Override to capture and reformat help output."""
        # Get the original help text
        help_text = super().format_help()
        
        # Check if this is a subcommand (not main command)
        if ' ' in self._prog:
            # Capture console output
            from io import StringIO
            buffer = StringIO()
            rich_console = Console(file=buffer, force_terminal=True, width=100)
            
            # Split into sections
            lines = help_text.split('\n')
            
            in_usage = False
            in_description = False
            in_positional = False
            in_options = False
            in_examples = False
            
            description_lines = []
            
            for line in lines:
                stripped = line.strip()
                
                # Usage section
                if line.startswith('usage:'):
                    rich_console.print()
                    rich_console.print(f"[bold cyan]{line}[/bold cyan]")
                    rich_console.print()
                    in_usage = True
                    continue
                
                # Section headers
                if stripped in ['positional arguments:', 'arguments:']:
                    if description_lines:
                        desc_text = ' '.join(description_lines)
                        rich_console.print(f"[dim]{desc_text}[/dim]")
                        rich_console.print()
                        description_lines = []
                    rich_console.print("[bold yellow]Positional Arguments[/bold yellow]")
                    rich_console.print()
                    in_positional = True
                    in_description = False
                    in_options = False
                    continue
                
                if stripped in ['options:', 'optional arguments:']:
                    if description_lines:
                        desc_text = ' '.join(description_lines)
                        rich_console.print(f"[dim]{desc_text}[/dim]")
                        rich_console.print()
                        description_lines = []
                    rich_console.print("[bold yellow]Options[/bold yellow]")
                    rich_console.print()
                    in_options = True
                    in_positional = False
                    in_description = False
                    continue
                
                if stripped.startswith('Examples:'):
                    rich_console.print()
                    rich_console.print("[bold yellow]Examples[/bold yellow]")
                    rich_console.print()
                    in_examples = True
                    in_options = False
                    continue
                
                # Handle content
                if in_examples:
                    if stripped.startswith('contextinator'):
                        rich_console.print(f"  [cyan]{stripped}[/cyan]")
                    elif stripped:
                        rich_console.print(f"  {stripped}")
                    continue
                
                if in_positional or in_options:
                    if not stripped:
                        rich_console.print()
                        continue
                    
                    # Argument name/flags
                    if line.startswith('  ') and not line.startswith('    '):
                        if '-' in stripped[:10]:  # It's a flag
                            rich_console.print(f"  [green]{stripped}[/green]")
                        else:
                            rich_console.print(f"  [cyan]{stripped}[/cyan]")
                    # Help text (indented more)
                    elif line.startswith('    '):
                        rich_console.print(f"      [dim]{stripped}[/dim]")
                    continue
                
                # Description (after usage, before first section)
                if in_usage and stripped and not stripped.endswith(':'):
                    description_lines.append(stripped)
            
            rich_console.print()
            return buffer.getvalue()
        
        # For main help or other cases, return original
        return help_text


def print_main_help():
    """Print the main help message with rich formatting."""
    
    # Header
    console.print()
    console.print(
        """[bold bright_magenta]
 _____             _            _   _             _             
/  __ \           | |          | | (_)           | |            
| /  \/ ___  _ __ | |_ _____  _| |_ _ _ __   __ _| |_ ___  _ __ 
| |    / _ \| '_ \| __/ _ \ \/ / __| | '_ \ / _` | __/ _ \| '__|
| \__/\ (_) | | | | ||  __/>  <| |_| | | | | (_| | || (_) | |   
 \____/\___/|_| |_|\__\___/_/\_\\___|_|_| |_|\__,_|\__\___/|_|   
                                                                
                                                                                                                                                                                                                   
[/bold bright_magenta]"""
    )
    console.print()
    
    # Quick Start Guide
    console.print("[bold yellow]🚀 Quick Start Guide[/bold yellow]")
    console.print()
    console.print("  [dim]For first-time users, follow this typical workflow:[/dim]")
    console.print()
    console.print("  [bold green]1.[/bold green] Process a repository (all-in-one):")
    console.print("     [cyan]contextinator chunk-embed-store-embeddings --repo-url <URL> --save[/cyan]")
    console.print()
    console.print("  [bold green]2.[/bold green] Search the codebase:")
    console.print("     [cyan]contextinator search \"your query\" -c <repo-name>[/cyan]")
    console.print()
    
    # Command Groups
    console.print("[bold yellow]📚 Available Commands[/bold yellow]")
    console.print()
    
    # Processing Commands
    processing_table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED,
        title="[bold]📦 Processing Commands[/bold]",
        title_style="bold blue",
        title_justify="left"
    )
    processing_table.add_column("Command", style="cyan", width=35)
    processing_table.add_column("Description", style="white")
    
    processing_table.add_row(
        "chunk",
        "Break codebase into semantic chunks"
    )
    processing_table.add_row(
        "embed",
        "Generate embeddings for chunks using OpenAI"
    )
    processing_table.add_row(
        "store-embeddings",
        "Store embeddings in ChromaDB vector database"
    )
    processing_table.add_row(
        "[bold green]chunk-embed-store-embeddings[/bold green]",
        "[bold]All-in-one: chunk → embed → store (recommended)[/bold]"
    )
    console.print(processing_table)
    console.print()
    
    # Search Commands
    search_table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED,
        title="[bold]🔍 Search Commands[/bold]",
        title_style="bold blue",
        title_justify="left"
    )
    search_table.add_column("Command", style="cyan", width=35)
    search_table.add_column("Description", style="white")
    
    search_table.add_row(
        "search",
        "Semantic search using natural language"
    )
    search_table.add_row(
        "symbol",
        "Find functions/classes by name"
    )
    search_table.add_row(
        "pattern",
        "Search for text patterns or regex"
    )
    search_table.add_row(
        "read-file",
        "Reconstruct complete file from chunks"
    )
    search_table.add_row(
        "search-advanced",
        "Advanced search with multiple filters"
    )
    console.print(search_table)
    console.print()
    
    # Database Commands
    db_table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED,
        title="[bold]🗄️  Database Management[/bold]",
        title_style="bold blue",
        title_justify="left"
    )
    db_table.add_column("Command", style="cyan", width=35)
    db_table.add_column("Description", style="white")
    
    db_table.add_row(
        "db-info",
        "Show database information and statistics"
    )
    db_table.add_row(
        "db-list",
        "List all collections"
    )
    db_table.add_row(
        "db-show",
        "Show details of a specific collection"
    )
    db_table.add_row(
        "db-clear",
        "Delete a specific collection"
    )
    console.print(db_table)
    console.print()
    
    # Examples
    console.print("[bold yellow]💡 Example Usage[/bold yellow]")
    console.print()
    
    examples = [
        ("Process a GitHub repository", "contextinator chunk-embed-store-embeddings --repo-url https://github.com/user/repo --save"),
        ("Process local directory", "contextinator chunk-embed-store-embeddings --path /path/to/repo --save"),
        ("Search for authentication code", "contextinator search \"authentication logic\" -c MyRepo -n 5"),
        ("Find a specific function", "contextinator symbol authenticate_user -c MyRepo"),
        ("Search with filters", "contextinator search-advanced -c MyRepo --semantic \"error handling\" --language python"),
        ("View database collections", "contextinator db-list"),
    ]
    
    for desc, cmd in examples:
        console.print(f"  [dim]{desc}:[/dim]")
        console.print(f"  [green]{cmd}[/green]")
        console.print()
    
    # Footer
    console.print("[bold yellow]ℹ️  Help & Documentation[/bold yellow]")
    console.print()
    console.print("  For detailed help on any command:")
    console.print("  [cyan]contextinator <command> --help[/cyan]")
    console.print()
    console.print("  Example: [cyan]contextinator search --help[/cyan]")
    console.print()


def print_command_group_help(title, commands_info):
    """
    Print help for a specific command group.
    
    Args:
        title: Group title
        commands_info: List of tuples (command_name, description)
    """
    console.print()
    console.print(f"[bold yellow]{title}[/bold yellow]")
    console.print()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")
    
    for cmd, desc in commands_info:
        table.add_row(cmd, desc)
    
    console.print(table)
    console.print()
