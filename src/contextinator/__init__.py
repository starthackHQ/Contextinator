"""
Contextinator v2.0 - Filesystem Tools for AI Agents

Primary interface: fs_read tool with Line/Directory/Search modes
Secondary interface: RAG module (existing v1 functionality)
"""

__version__ = "1.2.9"

from .tools import fs_read

# RAG module available as contextinator.rag
from . import rag

__all__ = ["fs_read", "rag", "__version__"]
