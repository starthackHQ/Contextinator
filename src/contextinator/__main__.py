"""
Entry point for running Contextinator as a module.

This allows the package to be executed with:
    python -m contextinator <command> [options]

This is the recommended way to run Contextinator when installed as a package.
"""

from .cli import main

if __name__ == '__main__':
    main()
