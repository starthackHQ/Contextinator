"""
Embedding service module for Contextinator.

This module provides functionality to generate embeddings for code chunks
using OpenAI's embedding API, with batch processing and error handling.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import openai

from ..config import (
    EMBEDDING_BATCH_SIZE,
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    OPENAI_MAX_TOKENS,
    get_storage_path,
)
from ..utils import ProgressTracker, logger
from ..utils.exceptions import ValidationError, FileSystemError


class EmbeddingService:
    """
    Service for generating embeddings using OpenAI API.
    
    Handles batch processing, validation, and error recovery for
    embedding generation with proper rate limiting and token management.
    """
    
    def __init__(self) -> None:
        """
        Initialize the embedding service.
        
        Raises:
            ValueError: If OpenAI API key is not configured
            RuntimeError: If OpenAI client initialization fails
        """
        self.client: Optional[openai.OpenAI] = None
        self._validate_api_key()
        self._initialize_client()
    
    def _validate_api_key(self) -> None:
        """
        Validate that OpenAI API key is available.
        
        Raises:
            ValueError: If API key is not set
        """
        if not OPENAI_API_KEY:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY in your .env file."
            )
    
    def _initialize_client(self) -> None:
        """
        Initialize OpenAI client and test connection.
        
        Raises:
            RuntimeError: If client initialization or connection test fails
        """
        try:
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            self._test_connection()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def _test_connection(self) -> None:
        """
        Test the OpenAI API connection with a minimal request.
        
        Raises:
            RuntimeError: If connection test fails
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
            
        try:
            response = self.client.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input="test connection"
            )
            if not response.data:
                raise RuntimeError("Invalid response from OpenAI API")
        except Exception as e:
            raise RuntimeError(f"OpenAI API connection test failed: {str(e)}")
    
    def _validate_chunk_content(self, content: str) -> tuple[bool, str]:
        """
        Validate and potentially fix chunk content for embedding generation.
        
        Args:
            content: Chunk content to validate
            
        Returns:
            Tuple of (is_valid, processed_content)
        """
        if not content or not content.strip():
            return False, content
        
        # Rough token estimation (4 chars per token average)
        estimated_tokens = len(content) // 4
        if estimated_tokens > OPENAI_MAX_TOKENS:
            # Fallback - truncate oversized content
            logger.warning(f"Chunk exceeds token limit ({estimated_tokens} estimated tokens), truncating")
            # Truncate to roughly 90% of limit to be safe
            max_chars = int(OPENAI_MAX_TOKENS * 4 * 0.9)
            truncated_content = content[:max_chars] + "\n... (truncated)"
            return True, truncated_content
        
        return True, content
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of chunks with batch processing and error recovery.
        
        Args:
            chunks: List of chunk dictionaries containing 'content' field
            
        Returns:
            List of chunks with added 'embedding' field
            
        Raises:
            EmbeddingError: If no valid chunks found or all batches fail
        """
        from ..utils.exceptions import EmbeddingError
        
        if not chunks:
            logger.info("No chunks provided for embedding generation")
            return []
        
        logger.info(f"🚀 Starting embedding generation for {len(chunks)} chunks...")
        logger.info(f"📊 Using model: {OPENAI_EMBEDDING_MODEL}")
        logger.info(f"📦 Batch size: {EMBEDDING_BATCH_SIZE}")
        
        # Validate and filter chunks with content fixing
        valid_chunks: List[Tuple[int, Dict[str, Any]]] = []
        fixed_chunks = 0
        
        for i, chunk in enumerate(chunks):
            content = chunk.get('content', '')
            is_valid, processed_content = self._validate_chunk_content(content)
            
            if is_valid:
                # Update chunk with processed content if it was modified
                if processed_content != content:
                    chunk = chunk.copy()
                    chunk['content'] = processed_content
                    fixed_chunks += 1
                    
                valid_chunks.append((i, chunk))
            else:
                logger.debug(f"Skipping invalid chunk at index {i}")
        
        if not valid_chunks:
            raise EmbeddingError("No valid chunks found for embedding generation")
        
        if fixed_chunks > 0:
            logger.info(f"📝 Fixed {fixed_chunks} oversized chunks by truncation")
        
        logger.info(f"✅ Processing {len(valid_chunks)} valid chunks")
        
        # Process in batches, continue on failures
        embedded_chunks = []
        failed_batches = []
        total_batches = (len(valid_chunks) + EMBEDDING_BATCH_SIZE - 1) // EMBEDDING_BATCH_SIZE
        progress = ProgressTracker(total_batches, "Generating embeddings")
        
        for batch_idx in range(0, len(valid_chunks), EMBEDDING_BATCH_SIZE):
            batch_end = min(batch_idx + EMBEDDING_BATCH_SIZE, len(valid_chunks))
            batch_chunks = valid_chunks[batch_idx:batch_end]
            
            try:
                batch_embeddings = self._generate_batch_embeddings(batch_chunks)
                embedded_chunks.extend(batch_embeddings)
                progress.update()
            except Exception as e:
                # Log batch failure and continue with other batches
                batch_num = batch_idx // EMBEDDING_BATCH_SIZE + 1
                logger.warning(f"Batch {batch_num}/{total_batches} failed, skipping {len(batch_chunks)} chunks: {e}")
                failed_batches.append(batch_num)
                progress.update()
                continue
        
        progress.finish()
        
        # Report results
        if failed_batches:
            logger.warning(f"Failed to process {len(failed_batches)} batches: {failed_batches}")
        
        if not embedded_chunks:
            raise EmbeddingError("All embedding batches failed - no embeddings generated")
        
        logger.info(f"✅ Successfully generated embeddings for {len(embedded_chunks)} chunks")
        if len(embedded_chunks) < len(valid_chunks):
            logger.warning(f"⚠️  {len(valid_chunks) - len(embedded_chunks)} chunks failed embedding generation")
        
        return embedded_chunks
    
    def _generate_batch_embeddings(self, batch_chunks: List[Tuple[int, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a batch of chunks with retry logic.
        
        Args:
            batch_chunks: List of (index, chunk) tuples
            
        Returns:
            List of chunks with embeddings
            
        Raises:
            EmbeddingError: If API call fails after retries
        """
        from ..utils.exceptions import EmbeddingError
        import time
        
        if not self.client:
            raise EmbeddingError("OpenAI client not initialized")
            
        batch_content = [chunk[1]['content'] for chunk in batch_chunks]
        max_retries = 3

        # Retry with exponential backoff
        for attempt in range(max_retries):
            try:
                response = self.client.embeddings.create(
                    model=OPENAI_EMBEDDING_MODEL,
                    input=batch_content
                )
                
                if not response.data or len(response.data) != len(batch_content):
                    raise EmbeddingError("Invalid response from OpenAI API - mismatched data length")
                
                embedded_chunks = []
                for (original_idx, chunk), embedding_data in zip(batch_chunks, response.data):
                    chunk_with_embedding = chunk.copy()
                    chunk_with_embedding['embedding'] = embedding_data.embedding
                    chunk_with_embedding['embedding_model'] = OPENAI_EMBEDDING_MODEL
                    chunk_with_embedding['original_index'] = original_idx
                    embedded_chunks.append(chunk_with_embedding)
                
                return embedded_chunks
                
            except Exception as e:
                # Determine if error is retryable
                is_retryable = self._is_retryable_error(e)
                
                if attempt < max_retries - 1 and is_retryable:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    # Final attempt or non-retryable error
                    error_msg = f"OpenAI API call failed: {e}"
                    if attempt == max_retries - 1:
                        error_msg = f"OpenAI API call failed after {max_retries} attempts: {e}"
                    raise EmbeddingError(error_msg, str(e))
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable.
        
        Args:
            error: Exception that occurred
            
        Returns:
            True if error should be retried, False otherwise
        """
        import openai
        
        # Retryable errors: rate limits, temporary server issues, network issues
        retryable_types = (
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.InternalServerError,
            openai.APIConnectionError,
        )
        
        # Non-retryable errors: authentication, invalid requests, etc.
        non_retryable_types = (
            openai.AuthenticationError,
            openai.PermissionDeniedError,
            openai.BadRequestError,
        )
        
        if isinstance(error, retryable_types):
            return True
        elif isinstance(error, non_retryable_types):
            return False
        else:
            # For unknown errors, be conservative and retry
            return True


def embed_chunks(
    base_dir: Union[str, Path], 
    repo_name: str, 
    save: bool = False, 
    chunks_data: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Generate embeddings for repository chunks.
    
    Args:
        base_dir: Base directory containing .chunks folder
        repo_name: Repository name for isolation
        save: Whether to save embeddings to disk
        chunks_data: Optional pre-loaded chunks data
    
    Returns:
        List of embedded chunks
        
    Raises:
        ValueError: If repo_name is empty
        FileNotFoundError: If chunks file not found and chunks_data not provided
        RuntimeError: If embedding generation fails
    """
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    if chunks_data is None:
        chunks_data = load_chunks(base_dir, repo_name)
    
    if not chunks_data:
        logger.info("No chunks found to embed")
        return []
    
    embedding_service = EmbeddingService()
    embedded_chunks = embedding_service.generate_embeddings(chunks_data)
    
    if save:
        save_embeddings(embedded_chunks, base_dir, repo_name)
    
    return embedded_chunks


def load_chunks(base_dir: Union[str, Path], repo_name: str) -> List[Dict[str, Any]]:
    """
    Load chunks from repository-specific directory.
    
    Args:
        base_dir: Base directory containing .chunks folder
        repo_name: Repository name for isolation
    
    Returns:
        List of chunks
        
    Raises:
        ValueError: If repo_name is empty
        FileNotFoundError: If chunks file doesn't exist
        json.JSONDecodeError: If chunks file is corrupted
    """
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    chunks_file = get_storage_path(base_dir, 'chunks', repo_name) / 'chunks.json'
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
    
    logger.info(f"📂 Loading chunks from {chunks_file}")
    
    try:
        with open(chunks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both old and new format
        if isinstance(data, list):
            chunks = data
        else:
            chunks = data.get('chunks', [])
        
        logger.info(f"📊 Loaded {len(chunks)} chunks")
        return chunks
        
    except json.JSONDecodeError as e:
        logger.error(f"Corrupted chunks file {chunks_file}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading chunks from {chunks_file}: {e}")
        raise


def save_embeddings(
    embedded_chunks: List[Dict[str, Any]], 
    base_dir: Union[str, Path], 
    repo_name: str
) -> Path:
    """
    Save embeddings to repository-specific directory.
    
    Args:
        embedded_chunks: List of embedded chunks
        base_dir: Base directory
        repo_name: Repository name for isolation
        
    Returns:
        Path to saved embeddings file
        
    Raises:
        ValueError: If repo_name is empty or embedded_chunks is empty
        OSError: If unable to create directory or write file
    """
    if not repo_name:
        raise ValidationError("Repository name cannot be empty", "repo_name", "non-empty string")
    if not embedded_chunks:
        raise ValidationError("No embedded chunks to save", "embedded_chunks", "non-empty list")
        
    try:
        embeddings_dir = get_storage_path(base_dir, 'embeddings', repo_name)
        embeddings_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise FileSystemError(f"Cannot create embeddings directory: {e}", str(embeddings_dir), "create")
    
    output_file = embeddings_dir / 'embeddings.json'
    
    data = {
        'embeddings': embedded_chunks,
        'model': OPENAI_EMBEDDING_MODEL,
        'total_chunks': len(embedded_chunks),
        'repository': repo_name,
        'version': '1.0'
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Embeddings saved to {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Failed to save embeddings to {output_file}: {e}")
        raise


def load_embeddings(base_dir: Union[str, Path], repo_name: str) -> List[Dict[str, Any]]:
    """
    Load embeddings from repository-specific directory.
    
    Args:
        base_dir: Base directory containing .embeddings folder
        repo_name: Repository name for isolation
    
    Returns:
        List of embeddings
        
    Raises:
        ValueError: If repo_name is empty
        FileNotFoundError: If embeddings file doesn't exist
        json.JSONDecodeError: If embeddings file is corrupted
    """
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    embeddings_file = get_storage_path(base_dir, 'embeddings', repo_name) / 'embeddings.json'
    
    if not embeddings_file.exists():
        raise FileNotFoundError(f"Embeddings file not found: {embeddings_file}")
    
    logger.info(f"📂 Loading embeddings from {embeddings_file}")
    
    try:
        with open(embeddings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both old and new format
        if isinstance(data, list):
            return data
        return data.get('embeddings', [])
        
    except json.JSONDecodeError as e:
        logger.error(f"Corrupted embeddings file {embeddings_file}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading embeddings from {embeddings_file}: {e}")
        raise


__all__ = [
    'EmbeddingService',
    'embed_chunks',
    'load_chunks',
    'load_embeddings',
    'save_embeddings',
]
