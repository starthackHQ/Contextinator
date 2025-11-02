"""
Embedding service module for Contextinator.

This module provides functionality to generate embeddings for code chunks
using OpenAI's embedding API, with batch processing and error handling.
"""

import json
import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import openai

from ..config import (
    CHUNKS_DIR,
    EMBEDDING_BATCH_SIZE,
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    OPENAI_MAX_TOKENS,
    get_storage_path,
)
from ..utils import ProgressTracker, logger
from ..utils.exceptions import ValidationError, FileSystemError


class EmbeddingService:
    """Service for generating embeddings using OpenAI API with async support."""
    
    def __init__(self) -> None:
        """Initialize the embedding service."""
        self.client: Optional[openai.OpenAI] = None
        self.async_client: Optional[openai.AsyncOpenAI] = None
        self._validate_api_key()
        self._initialize_client()
    
    def _validate_api_key(self) -> None:
        """Validate that OpenAI API key is available."""
        if not OPENAI_API_KEY:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY in your .env file."
            )
    
    def _initialize_client(self) -> None:
        """Initialize OpenAI clients (sync and async)."""
        try:
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            self.async_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
            self._test_connection()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def _test_connection(self) -> None:
        """Test the OpenAI API connection."""
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
    
    def _validate_chunk_content(self, content: str) -> Tuple[bool, str]:
        """Validate and potentially fix chunk content."""
        if not content or not content.strip():
            return False, content
        
        estimated_tokens = len(content) // 4
        if estimated_tokens > OPENAI_MAX_TOKENS:
            logger.warning(f"Chunk exceeds token limit ({estimated_tokens} estimated tokens), truncating")
            max_chars = int(OPENAI_MAX_TOKENS * 4 * 0.9)
            truncated_content = content[:max_chars] + "\n... (truncated)"
            return True, truncated_content
        
        return True, content
    
    async def _generate_batch_embeddings_async(self, batch_chunks: List[Tuple[int, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Generate embeddings for a batch asynchronously."""
        batch_content = [chunk[1]['content'] for chunk in batch_chunks]
        
        try:
            response = await self.async_client.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input=batch_content
            )
            
            if not response.data or len(response.data) != len(batch_content):
                raise RuntimeError("Invalid response from OpenAI API")
            
            embedded_chunks = []
            for (original_idx, chunk), embedding_data in zip(batch_chunks, response.data):
                chunk_with_embedding = chunk.copy()
                chunk_with_embedding['embedding'] = embedding_data.embedding
                chunk_with_embedding['embedding_model'] = OPENAI_EMBEDDING_MODEL
                chunk_with_embedding['original_index'] = original_idx
                embedded_chunks.append(chunk_with_embedding)
            
            return embedded_chunks
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {str(e)}")
    
    async def generate_embeddings_async(self, chunks: List[Dict[str, Any]], 
                                       max_concurrent: int = 10) -> List[Dict[str, Any]]:
        """Generate embeddings with async parallel batch processing."""
        if not chunks:
            logger.info("No chunks provided for embedding generation")
            return []
        
        logger.info(f"🚀 Starting async embedding generation for {len(chunks)} chunks...")
        logger.info(f"📊 Using model: {OPENAI_EMBEDDING_MODEL}")
        logger.info(f"📦 Batch size: {EMBEDDING_BATCH_SIZE}")
        logger.info(f"⚡ Max concurrent requests: {max_concurrent}")
        
        # Validate chunks
        valid_chunks = []
        fixed_chunks = 0
        
        for i, chunk in enumerate(chunks):
            content = chunk.get('content', '')
            is_valid, processed_content = self._validate_chunk_content(content)
            
            if is_valid:
                if processed_content != content:
                    chunk = chunk.copy()
                    chunk['content'] = processed_content
                    fixed_chunks += 1
                valid_chunks.append((i, chunk))
            else:
                logger.debug(f"Skipping invalid chunk at index {i}")
        
        if not valid_chunks:
            raise RuntimeError("No valid chunks found for embedding generation")
        
        if fixed_chunks > 0:
            logger.info(f"📝 Fixed {fixed_chunks} oversized chunks by truncation")
        
        logger.info(f"✅ Processing {len(valid_chunks)} valid chunks")
        
        # Create batches
        batches = []
        for batch_idx in range(0, len(valid_chunks), EMBEDDING_BATCH_SIZE):
            batch_end = min(batch_idx + EMBEDDING_BATCH_SIZE, len(valid_chunks))
            batches.append(valid_chunks[batch_idx:batch_end])
        
        # Process batches with concurrency limit
        embedded_chunks = []
        progress = ProgressTracker(len(batches), "Generating embeddings")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_batch_with_semaphore(batch):
            async with semaphore:
                return await self._generate_batch_embeddings_async(batch)
        
        tasks = [process_batch_with_semaphore(batch) for batch in batches]
        
        for coro in asyncio.as_completed(tasks):
            try:
                batch_result = await coro
                embedded_chunks.extend(batch_result)
                progress.update()
            except Exception as e:
                progress.finish()
                raise RuntimeError(f"Embedding generation failed: {str(e)}")
        
        progress.finish()
        logger.info(f"✅ Successfully generated embeddings for {len(embedded_chunks)} chunks")
        return embedded_chunks
    
    def _generate_embeddings_sync(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synchronous embedding generation with retry logic."""
        from ..utils.exceptions import EmbeddingError
        
        if not chunks:
            logger.info("No chunks provided for embedding generation")
            return []
        
        logger.info(f"🚀 Starting embedding generation for {len(chunks)} chunks...")
        logger.info(f"📊 Using model: {OPENAI_EMBEDDING_MODEL}")
        logger.info(f"📦 Batch size: {EMBEDDING_BATCH_SIZE}")
        
        # Validate chunks
        valid_chunks = []
        fixed_chunks = 0
        
        for i, chunk in enumerate(chunks):
            content = chunk.get('content', '')
            is_valid, processed_content = self._validate_chunk_content(content)
            
            if is_valid:
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
        
        # Process in batches
        embedded_chunks = []
        failed_batches = []
        total_batches = (len(valid_chunks) + EMBEDDING_BATCH_SIZE - 1) // EMBEDDING_BATCH_SIZE
        progress = ProgressTracker(total_batches, "Generating embeddings")
        
        for batch_idx in range(0, len(valid_chunks), EMBEDDING_BATCH_SIZE):
            batch_end = min(batch_idx + EMBEDDING_BATCH_SIZE, len(valid_chunks))
            batch_chunks = valid_chunks[batch_idx:batch_end]
            
            try:
                batch_embeddings = self._generate_batch_embeddings_sync(batch_chunks)
                embedded_chunks.extend(batch_embeddings)
                progress.update()
            except Exception as e:
                batch_num = batch_idx // EMBEDDING_BATCH_SIZE + 1
                logger.warning(f"Batch {batch_num}/{total_batches} failed: {e}")
                failed_batches.append(batch_num)
                progress.update()
        
        progress.finish()
        
        if failed_batches:
            logger.warning(f"Failed to process {len(failed_batches)} batches: {failed_batches}")
        
        if not embedded_chunks:
            raise EmbeddingError("All embedding batches failed")
        
        logger.info(f"✅ Successfully generated embeddings for {len(embedded_chunks)} chunks")
        return embedded_chunks
    
    def _generate_batch_embeddings_sync(self, batch_chunks: List[Tuple[int, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Generate embeddings for a batch with retry logic."""
        from ..utils.exceptions import EmbeddingError
        
        if not self.client:
            raise EmbeddingError("OpenAI client not initialized")
            
        batch_content = [chunk[1]['content'] for chunk in batch_chunks]
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.client.embeddings.create(
                    model=OPENAI_EMBEDDING_MODEL,
                    input=batch_content
                )
                
                if not response.data or len(response.data) != len(batch_content):
                    raise EmbeddingError("Invalid response from OpenAI API")
                
                embedded_chunks = []
                for (original_idx, chunk), embedding_data in zip(batch_chunks, response.data):
                    chunk_with_embedding = chunk.copy()
                    chunk_with_embedding['embedding'] = embedding_data.embedding
                    chunk_with_embedding['embedding_model'] = OPENAI_EMBEDDING_MODEL
                    chunk_with_embedding['original_index'] = original_idx
                    embedded_chunks.append(chunk_with_embedding)
                
                return embedded_chunks
                
            except Exception as e:
                is_retryable = self._is_retryable_error(e)
                
                if attempt < max_retries - 1 and is_retryable:
                    wait_time = 2 ** attempt
                    logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    error_msg = f"OpenAI API call failed after {max_retries} attempts: {e}"
                    raise EmbeddingError(error_msg, str(e))
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable."""
        retryable_types = (
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.InternalServerError,
            openai.APIConnectionError,
        )
        
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
            return True
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]], 
                           use_async: bool = True, max_concurrent: int = 10) -> List[Dict[str, Any]]:
        """Generate embeddings (wrapper for sync/async)."""
        if use_async:
            return asyncio.run(self.generate_embeddings_async(chunks, max_concurrent))
        else:
            return self._generate_embeddings_sync(chunks)


def embed_chunks(
    base_dir: Union[str, Path], 
    repo_name: str, 
    save: bool = False, 
    chunks_data: Optional[List[Dict[str, Any]]] = None,
    use_async: bool = True,
    max_concurrent: int = 10
) -> List[Dict[str, Any]]:
    """Generate embeddings for repository chunks."""
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    if chunks_data is None:
        chunks_data = load_chunks(base_dir, repo_name)
    
    if not chunks_data:
        logger.info("No chunks found to embed")
        return []
    
    embedding_service = EmbeddingService()
    embedded_chunks = embedding_service.generate_embeddings(
        chunks_data, use_async=use_async, max_concurrent=max_concurrent
    )
    
    if save:
        save_embeddings(embedded_chunks, base_dir, repo_name)
    
    return embedded_chunks


def load_chunks(base_dir: Union[str, Path], repo_name: str) -> List[Dict[str, Any]]:
    """Load chunks from repository-specific directory."""
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    chunks_file = get_storage_path(base_dir, 'chunks', repo_name) / 'chunks.json'
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
    
    logger.info(f"📂 Loading chunks from {chunks_file}")
    
    try:
        with open(chunks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
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
    """Save embeddings to repository-specific directory."""
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
    """Load embeddings from repository-specific directory."""
    if not repo_name:
        raise ValueError("Repository name cannot be empty")
        
    embeddings_file = get_storage_path(base_dir, 'embeddings', repo_name) / 'embeddings.json'
    
    if not embeddings_file.exists():
        raise FileNotFoundError(f"Embeddings file not found: {embeddings_file}")
    
    logger.info(f"📂 Loading embeddings from {embeddings_file}")
    
    try:
        with open(embeddings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
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
