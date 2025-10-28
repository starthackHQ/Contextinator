import os
import subprocess
from pathlib import Path


def setup_tree_sitter_languages():
    """
    Dynamically clone and build tree-sitter language parsers.
    Only runs once - checks if already built.
    """
    build_dir = Path('build')
    languages_so = build_dir / 'languages.so'
    
    # Check if already built
    if languages_so.exists():
        return True
    
    print("Setting up tree-sitter languages...")
    build_dir.mkdir(exist_ok=True)
    
    # Languages to build
    languages = {
        'python': 'https://github.com/tree-sitter/tree-sitter-python',
        'javascript': 'https://github.com/tree-sitter/tree-sitter-javascript',
        'typescript': 'https://github.com/tree-sitter/tree-sitter-typescript',
        'java': 'https://github.com/tree-sitter/tree-sitter-java',
        'go': 'https://github.com/tree-sitter/tree-sitter-go',
        'rust': 'https://github.com/tree-sitter/tree-sitter-rust',
        'cpp': 'https://github.com/tree-sitter/tree-sitter-cpp',
        'c': 'https://github.com/tree-sitter/tree-sitter-c',
    }
    
    try:
        from tree_sitter import Language
        
        # Clone repositories
        vendor_dir = build_dir / 'vendor'
        vendor_dir.mkdir(exist_ok=True)
        
        lang_paths = []
        for lang, repo_url in languages.items():
            lang_dir = vendor_dir / f'tree-sitter-{lang}'
            
            if not lang_dir.exists():
                print(f"Cloning {lang}...")
                subprocess.run(['git', 'clone', '--depth', '1', repo_url, str(lang_dir)], 
                             check=True, capture_output=True)
            
            # Handle special case for typescript which has different directory structure
            if lang == 'typescript':
                # TypeScript repo has typescript/ and tsx/ subdirectories
                lang_paths.append(str(lang_dir / 'typescript'))
                lang_paths.append(str(lang_dir / 'tsx'))
            else:
                lang_paths.append(str(lang_dir))
        
        # Build languages
        print("Building language parsers...")
        Language.build_library(str(languages_so), lang_paths)
        
        print("✅ Tree-sitter languages built successfully!")
        return True
        
    except Exception as e:
        print(f"⚠️  Failed to build tree-sitter languages: {e}")
        print("Falling back to basic file chunking")
        return False


def get_language(lang_name: str):
    """Get tree-sitter Language object for a language."""
    try:
        from tree_sitter import Language
        languages_so = Path('build/languages.so')
        
        if not languages_so.exists():
            setup_tree_sitter_languages()
        
        # Handle special case for tsx - it's part of the typescript repo
        if lang_name == 'tsx':
            return Language(str(languages_so), 'tsx')
        
        return Language(str(languages_so), lang_name)
    except Exception:
        return None
