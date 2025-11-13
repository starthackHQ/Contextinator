"""
Centralized logging configuration for Contextinator.

This module provides a configured logger instance and setup utilities
for consistent logging throughout the application.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "contextinator", level: str = "INFO") -> logging.Logger:
    """
    Setup and return a configured logger.
    
    Args:
        name: Logger name (default: "contextinator")
        level: Logging level (default: "INFO")
        
    Returns:
        Configured logger instance
        
    Raises:
        ValueError: If level is not a valid logging level
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Validate and set level
    try:
        numeric_level = getattr(logging, level.upper())
    except AttributeError:
        raise ValueError(f"Invalid logging level: {level}")
        
    logger.setLevel(numeric_level)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


# Global logger instance
logger: logging.Logger = setup_logger()


__all__ = ['setup_logger', 'logger']
