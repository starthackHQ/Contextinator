"""
Contextinator v2.0 - Filesystem Tools for AI Agents

Primary interface: fs_read tool with Line/Directory/Search modes
Secondary interface: RAG module (existing v1 functionality)
"""

__version__ = "2.0.1"

from .tools import fs_read

__all__ = ["fs_read", "__version__"]

def __getattr__(name):
    """Lazy import rag module to avoid chromadb dependency unless needed."""
    if name == "rag":
        from . import rag
        return rag
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
