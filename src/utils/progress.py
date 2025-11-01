"""
Progress tracking utilities for Contextinator.

This module provides a simple progress tracker for long-running operations
like chunking and embedding generation.
"""

from typing import Optional

from .logger import logger


class ProgressTracker:
    """
    Simple progress tracker for chunking operations.
    
    Provides console-based progress reporting with percentage completion
    and customizable descriptions.
    """
    
    def __init__(self, total: int, description: str = "Processing") -> None:
        """
        Initialize progress tracker.
        
        Args:
            total: Total number of items to process
            description: Description of the operation being tracked
            
        Raises:
            ValueError: If total is negative
        """
        if total < 0:
            raise ValueError("Total must be non-negative")
            
        self.total = total
        self.current = 0
        self.description = description
    
    def update(self, n: int = 1) -> None:
        """
        Update progress by n steps.
        
        Args:
            n: Number of steps to advance (default: 1)
            
        Raises:
            ValueError: If n is negative or would exceed total
        """
        if n < 0:
            raise ValueError("Progress increment must be non-negative")
            
        if self.current + n > self.total:
            logger.warning(f"Progress update would exceed total: {self.current + n} > {self.total}")
            n = self.total - self.current
            
        self.current += n
        percentage = (self.current / self.total * 100) if self.total > 0 else 0
        print(f"\r{self.description}: {self.current}/{self.total} ({percentage:.1f}%)", end='', flush=True)
    
    def finish(self) -> None:
        """Mark progress as complete and add newline."""
        print()  # New line after progress
        logger.debug(f"Progress tracking completed: {self.description}")


__all__ = ['ProgressTracker']
