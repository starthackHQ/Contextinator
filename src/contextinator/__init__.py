"""
Contextinator v2.0 - Filesystem Tools for AI Agents

Primary interface: fs_read tool with Line/Directory/Search modes
Secondary interface: RAG module (existing v1 functionality)
"""

__version__ = "2.0.0"

from .tools import fs_read

__all__ = ["fs_read", "__version__"]
