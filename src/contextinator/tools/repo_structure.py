"""Repository structure analyzer tool."""
from pathlib import Path
from typing import List, Optional
import json
import asyncio
from ..config import DEFAULT_IGNORE_PATTERNS
from ..utils.logger import logger


def should_ignore(path: Path, ignore_patterns: List[str]) -> bool:
    """Check if path matches ignore patterns."""
    name = path.name
    path_str = str(path)
    
    for pattern in ignore_patterns:
        if pattern.startswith('*'):
            if name.endswith(pattern[1:]):
                return True
        elif pattern in path_str or name == pattern:
            return True
    return False


def build_tree_dict(path: Path, ignore_patterns: List[str], max_depth: Optional[int] = None, current_depth: int = 0):
    """Build tree structure as dict."""
    if max_depth is not None and current_depth > max_depth:
        return None
    
    if should_ignore(path, ignore_patterns):
        return None
    
    result = {"name": path.name, "type": "dir" if path.is_dir() else "file"}
    
    if path.is_dir():
        children = []
        try:
            for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
                child = build_tree_dict(item, ignore_patterns, max_depth, current_depth + 1)
                if child:
                    children.append(child)
        except PermissionError:
            pass
        
        if children:
            result["children"] = children
    
    return result


def format_tree_string(node, prefix="", is_last=True):
    """Format tree dict as string with tree characters."""
    if not node:
        return ""
    
    lines = []
    connector = "└── " if is_last else "├── "
    name = node["name"] + ("/" if node["type"] == "dir" else "")
    
    lines.append(f"{prefix}{connector}{name}")
    
    if "children" in node:
        extension = "    " if is_last else "│   "
        children = node["children"]
        
        for i, child in enumerate(children):
            lines.append(format_tree_string(child, prefix + extension, i == len(children) - 1))
    
    return "\n".join(lines)


async def analyze_structure(
    repo_path: str,
    max_depth: Optional[int] = None,
    output_format: str = "tree",
    output_file: Optional[str] = None,
    ignore_patterns: Optional[List[str]] = None
) -> str:
    """Analyze repository structure (async)."""
    path = Path(repo_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {repo_path}")
    
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS
    
    logger.info(f"Analyzing structure: {path.name}")
    
    # Run in executor for true async
    loop = asyncio.get_event_loop()
    tree = await loop.run_in_executor(
        None,
        lambda: build_tree_dict(path, ignore_patterns, max_depth)
    )
    
    if output_format == "json":
        output = json.dumps(tree, indent=2)
    else:
        output = f"{path.name}/\n" + format_tree_string(tree, "", True)
    
    if output_file:
        await loop.run_in_executor(
            None,
            lambda: Path(output_file).write_text(output, encoding='utf-8')
        )
        logger.info(f"Saved to: {output_file}")
    
    return output


# Keep old name for compatibility
analyze_structure_async = analyze_structure

__all__ = ['analyze_structure', 'analyze_structure_async']
