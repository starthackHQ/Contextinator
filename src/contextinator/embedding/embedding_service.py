"""
Embedding service module for Contextinator.

This module provides functionality to generate embeddings for code chunks
using OpenAI's embedding API, with batch processing and error handling.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Lazy import openai (saves 2-3 seconds at startup)

from ..config import (
    EMBEDDING_BATCH_SIZE,
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    OPENAI_MAX_TOKENS,
    get_storage_path,
    validate_openai_api_key,
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
        """Initialize the embedding service."""
        # Lazy import openai here (not at module level)
        import openai
        
        self.client: Optional[openai.OpenAI] = None
        self._validate_api_key()
        self._initialize_client()
    
    def _validate_api_key(self) -> None:
        """
        Validate that OpenAI API key is available.
        
        Raises:
            ConfigurationError: If API key is not set
        """
        validate_openai_api_key()
    
    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        import openai
        try:
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            logger.info("✅ OpenAI client initialized")
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
    
    def _get_embedding_content(self, chunk: Dict[str, Any]) -> str:
        """
        Get the appropriate content for embedding generation.
        
        Prefers enriched_content (with context metadata) for better semantic search,
        falls back to regular content if enriched_content is not available.
        
        Args:
            chunk: Chunk dictionary
            
        Returns:
            Content string to use for embedding
        """
        # Prefer enriched content for semantic search quality
        return chunk.get('enriched_content', chunk.get('content', ''))
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]], use_async: bool = True, batch_size: int = 250, max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """Generate embeddings (async if use_async=True)."""
        if use_async:
            import asyncio
            # Check if already in async context to avoid nested event loop
            try:
                loop = asyncio.get_running_loop()
                # Already in async context - cannot use asyncio.run()
                raise RuntimeError(
                    "generate_embeddings called with use_async=True from async context. "
                    "Call _generate_embeddings_async() directly instead."
                )
            except RuntimeError as e:
                if "no running event loop" in str(e).lower():
                    # Not in async context - safe to use asyncio.run()
                    return asyncio.run(self._generate_embeddings_async(chunks, batch_size, max_concurrent))
                else:
                    # Already in async context
                    raise
        else:
            return self._generate_embeddings_sync(chunks)
    
    async def _generate_embeddings_async(self, chunks: List[Dict[str, Any]], batch_size: int, max_concurrent: int) -> List[Dict[str, Any]]:
        """Async embedding with concurrency and rate limiting."""
        from openai import AsyncOpenAI
        import asyncio
        from ..utils.exceptions import EmbeddingError
        
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Validate chunks
        logger.info(f"⏳ Validating {len(chunks)} chunks...")
        valid_chunks = []
        for i, chunk in enumerate(chunks):
            if i % 1000 == 0 and i > 0:
                logger.info(f"   Validated {i}/{len(chunks)} chunks...")
            content = self._get_embedding_content(chunk)
            is_valid, processed = self._validate_chunk_content(content)
            if is_valid:
                if processed != content:
                    chunk = chunk.copy()
                    if 'enriched_content' in chunk:
                        chunk['enriched_content'] = processed
                    else:
                        chunk['content'] = processed
                valid_chunks.append((i, chunk))
        
        if not valid_chunks:
            return []
        
        logger.info(f"🚀 Async embedding {len(valid_chunks)} chunks (batch={batch_size}, concurrent={max_concurrent})")
        
        async def embed_batch(batch):
            contents = [self._get_embedding_content(c) for _, c in batch]
            async with semaphore:
                for attempt in range(3):
                    try:
                        response = await client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=contents)
                        return [(idx, {**chunk, 'embedding': emb.embedding, 'embedding_model': OPENAI_EMBEDDING_MODEL}) 
                                for (idx, chunk), emb in zip(batch, response.data)]
                    except Exception as e:
                        if attempt < 2:
                            await asyncio.sleep(2 ** attempt)
                        else:
                            logger.error(f"❌ Batch failed after 3 attempts: {e}")
                            raise  # Re-raise to be caught by gather
        
        batches = [valid_chunks[i:i + batch_size] for i in range(0, len(valid_chunks), batch_size)]
        logger.info(f"📦 Processing {len(batches)} batches...")
        results = await asyncio.gather(*[embed_batch(b) for b in batches], return_exceptions=True)
        
        # Fail fast on errors instead of silent data loss
        embedded = []
        failed_batches = []
        for i, batch_result in enumerate(results):
            if isinstance(batch_result, Exception):
                failed_batches.append((i, str(batch_result)))
                logger.error(f"⚠️  Batch {i+1}/{len(batches)} failed: {batch_result}")
            else:
                embedded.extend([chunk for _, chunk in batch_result])
        
        if failed_batches:
            error_msg = f"{len(failed_batches)}/{len(batches)} batches failed"
            logger.error(f"❌ {error_msg}")
            raise EmbeddingError(f"Async embedding failed: {error_msg}")
        
        logger.info(f"✅ Embedded {len(embedded)} chunks")
        return embedded
    
    def _generate_embeddings_sync(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
            # Use enriched content if available, fall back to regular content
            content = self._get_embedding_content(chunk)
            is_valid, processed_content = self._validate_chunk_content(content)
            
            if is_valid:
                # Only update chunk if content was actually modified (avoid unnecessary copies)
                if processed_content is not content:  # Use identity check for performance
                    chunk = chunk.copy()
                    # Update the enriched_content field (or content if no enriched version)
                    if 'enriched_content' in chunk:
                        chunk['enriched_content'] = processed_content
                    else:
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
        
        Uses enriched_content field for embedding if available, otherwise falls back to content.
        
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
            
        # Use enriched content for embeddings (better semantic search)
        batch_content = [self._get_embedding_content(chunk[1]) for chunk in batch_chunks]
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
    chunks_data: Optional[List[Dict[str, Any]]] = None,
    custom_chunks_dir: Optional[str] = None,
    custom_embeddings_dir: Optional[str] = None,
    use_async: bool = True,
    batch_size: int = 250,
    max_concurrent: int = 5
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
        chunks_data = load_chunks(base_dir, repo_name, custom_chunks_dir)
    
    if not chunks_data:
        logger.info("No chunks found to embed")
        return []
    
    embedding_service = EmbeddingService()
    embedded_chunks = embedding_service.generate_embeddings(chunks_data, use_async, batch_size, max_concurrent)
    
    if save:
        save_embeddings(embedded_chunks, base_dir, repo_name, custom_embeddings_dir)
    
    return embedded_chunks


def load_chunks(base_dir: Union[str, Path], repo_name: str, custom_chunks_dir: Optional[str] = None) -> List[Dict[str, Any]]:
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
        
    chunks_file = get_storage_path(base_dir, 'chunks', repo_name, custom_chunks_dir) / 'chunks.json'
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
    
    logger.info(f"📂 Loading chunks from {chunks_file}")
    
    try:
        # Check file size
        file_size_mb = chunks_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 10:
            logger.warning(f"⚠️  Large chunks file ({file_size_mb:.1f}MB) - this may take a moment...")
        
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
    repo_name: str,
    custom_embeddings_dir: Optional[str] = None) -> Path:
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
        embeddings_dir = get_storage_path(base_dir, 'embeddings', repo_name, custom_embeddings_dir)
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
        import tempfile
        temp_fd, temp_path = tempfile.mkstemp(dir=embeddings_dir, suffix='.tmp')
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # Atomic rename
            os.replace(temp_path, output_file)
        except:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
        
        logger.info(f"💾 Embeddings saved to {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Failed to save embeddings to {output_file}: {e}")
        raise


def load_embeddings(base_dir: Union[str, Path], repo_name: str, custom_embeddings_dir: Optional[str] = None) -> List[Dict[str, Any]]:
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
        
    embeddings_file = get_storage_path(base_dir, 'embeddings', repo_name, custom_embeddings_dir) / 'embeddings.json'
    
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
