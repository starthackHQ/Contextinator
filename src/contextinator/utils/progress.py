"""
Progress tracking utilities for Contextinator.

This module provides a simple progress tracker for long-running operations
like chunking and embedding generation.
"""

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
            ValidationError: If total is negative
        """
        from .exceptions import ValidationError
        
        if total < 0:
            raise ValidationError("Total must be non-negative", "total", "non-negative integer")
            
        self.total = total
        self.current = 0
        self.description = description
    
    def update(self, n: int = 1) -> None:
        """
        Update progress by n steps.
        
        Args:
            n: Number of steps to advance (default: 1)
            
        Raises:
            ValidationError: If n is negative or would exceed total
        """
        from .exceptions import ValidationError
        
        if n < 0:
            raise ValidationError("Progress increment must be non-negative", "n", "non-negative integer")
            
        if self.current + n > self.total:
            logger.warning(f"Progress update would exceed total: {self.current + n} > {self.total}")
            n = self.total - self.current
            
        self.current += n
        percentage = (self.current / self.total * 100) if self.total > 0 else 0
        
        # Log progress updates
        logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")
    
    def finish(self) -> None:
        """Mark progress as complete."""
        logger.info(f"✅ {self.description} completed: {self.current}/{self.total}")
        logger.debug(f"Progress tracking completed: {self.description}")


__all__ = ['ProgressTracker']
