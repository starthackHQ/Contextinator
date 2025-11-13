"""
Custom exception classes for Contextinator.

This module provides a hierarchy of custom exceptions for different
error scenarios throughout the application, enabling precise error
handling and user-friendly error messages.
"""

from typing import Optional


class ContextinatorError(Exception):
    """
    Base exception class for all Contextinator-specific errors.
    
    Provides a foundation for all custom exceptions with optional
    error codes and user-friendly messages.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None) -> None:
        """
        Initialize the base exception.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self) -> str:
        """Return formatted error message."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigurationError(ContextinatorError):
    """
    Raised when there are configuration-related errors.
    
    Examples:
        - Missing required environment variables
        - Invalid configuration values
        - Missing configuration files
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None) -> None:
        """
        Initialize configuration error.
        
        Args:
            message: Error description
            config_key: Optional configuration key that caused the error
        """
        super().__init__(message, "CONFIG_ERROR")
        self.config_key = config_key


class ParsingError(ContextinatorError):
    """
    Raised when file parsing or AST generation fails.
    
    Examples:
        - Unsupported file types
        - Corrupted source files
        - Tree-sitter parsing failures
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None, language: Optional[str] = None) -> None:
        """
        Initialize parsing error.
        
        Args:
            message: Error description
            file_path: Optional path to file that failed to parse
            language: Optional programming language
        """
        super().__init__(message, "PARSE_ERROR")
        self.file_path = file_path
        self.language = language


class EmbeddingError(ContextinatorError):
    """
    Raised when embedding generation or processing fails.
    
    Examples:
        - OpenAI API failures
        - Invalid embedding data
        - Token limit exceeded
    """
    
    def __init__(self, message: str, api_error: Optional[str] = None) -> None:
        """
        Initialize embedding error.
        
        Args:
            message: Error description
            api_error: Optional underlying API error message
        """
        super().__init__(message, "EMBEDDING_ERROR")
        self.api_error = api_error


class VectorStoreError(ContextinatorError):
    """
    Raised when vector store operations fail.
    
    Examples:
        - ChromaDB connection failures
        - Collection creation errors
        - Data storage/retrieval failures
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, collection: Optional[str] = None) -> None:
        """
        Initialize vector store error.
        
        Args:
            message: Error description
            operation: Optional operation that failed (store, retrieve, etc.)
            collection: Optional collection name
        """
        super().__init__(message, "VECTORSTORE_ERROR")
        self.operation = operation
        self.collection = collection


class SearchError(ContextinatorError):
    """
    Raised when search operations fail.
    
    Examples:
        - Invalid search queries
        - Collection not found
        - Search backend failures
    """
    
    def __init__(self, message: str, query: Optional[str] = None, search_type: Optional[str] = None) -> None:
        """
        Initialize search error.
        
        Args:
            message: Error description
            query: Optional search query that failed
            search_type: Optional type of search (semantic, regex, etc.)
        """
        super().__init__(message, "SEARCH_ERROR")
        self.query = query
        self.search_type = search_type


class FileSystemError(ContextinatorError):
    """
    Raised when file system operations fail.
    
    Examples:
        - File not found
        - Permission denied
        - Disk space issues
    """
    
    def __init__(self, message: str, path: Optional[str] = None, operation: Optional[str] = None) -> None:
        """
        Initialize file system error.
        
        Args:
            message: Error description
            path: Optional file/directory path
            operation: Optional operation that failed (read, write, create, etc.)
        """
        super().__init__(message, "FILESYSTEM_ERROR")
        self.path = path
        self.operation = operation


class ValidationError(ContextinatorError):
    """
    Raised when input validation fails.
    
    Examples:
        - Invalid function parameters
        - Malformed data structures
        - Type mismatches
    """
    
    def __init__(self, message: str, parameter: Optional[str] = None, expected_type: Optional[str] = None) -> None:
        """
        Initialize validation error.
        
        Args:
            message: Error description
            parameter: Optional parameter name that failed validation
            expected_type: Optional expected type/format
        """
        super().__init__(message, "VALIDATION_ERROR")
        self.parameter = parameter
        self.expected_type = expected_type


__all__ = [
    'ContextinatorError',
    'ConfigurationError',
    'EmbeddingError',
    'FileSystemError',
    'ParsingError',
    'SearchError',
    'ValidationError',
    'VectorStoreError',
]
