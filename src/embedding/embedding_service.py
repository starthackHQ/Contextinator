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
    CHUNKS_DIR,
    EMBEDDING_BATCH_SIZE,
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    OPENAI_MAX_TOKENS,
    get_storage_path,
)
from ..utils import ProgressTracker, logger


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
    
    def _validate_chunk_content(self, content: str) -> bool:
        """
        Validate chunk content for embedding generation.
        
        Args:
            content: Chunk content to validate
            
        Returns:
            True if content is valid for embedding, False otherwise
        """
        if not content or not content.strip():
            return False
        
        # Rough token estimation (4 chars per token average)
        estimated_tokens = len(content) // 4
        if estimated_tokens > OPENAI_MAX_TOKENS:
            logger.warning(f"Chunk may exceed token limit ({estimated_tokens} estimated tokens)")
            return False
        
        return True
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of chunks with batch processing.
        
        Args:
            chunks: List of chunk dictionaries containing 'content' field
            
        Returns:
            List of chunks with added 'embedding' field
            
        Raises:
            RuntimeError: If no valid chunks found or embedding generation fails
        """
        if not chunks:
            logger.info("No chunks provided for embedding generation")
            return []
        
        logger.info(f"🚀 Starting embedding generation for {len(chunks)} chunks...")
        logger.info(f"📊 Using model: {OPENAI_EMBEDDING_MODEL}")
        logger.info(f"📦 Batch size: {EMBEDDING_BATCH_SIZE}")
        
        # Validate and filter chunks
        valid_chunks: List[Tuple[int, Dict[str, Any]]] = []
        for i, chunk in enumerate(chunks):
            content = chunk.get('content', '')
            if self._validate_chunk_content(content):
                valid_chunks.append((i, chunk))
            else:
                logger.debug(f"Skipping invalid chunk at index {i}")
        
        if not valid_chunks:
            raise RuntimeError("No valid chunks found for embedding generation")
        
        logger.info(f"✅ Processing {len(valid_chunks)} valid chunks")
        
        # Process in batches
        embedded_chunks = []
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
                progress.finish()
                raise RuntimeError(f"Embedding generation failed at batch {batch_idx//EMBEDDING_BATCH_SIZE + 1}: {str(e)}")
        
        progress.finish()
        logger.info(f"✅ Successfully generated embeddings for {len(embedded_chunks)} chunks")
        return embedded_chunks
    
    def _generate_batch_embeddings(self, batch_chunks: List[Tuple[int, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a batch of chunks.
        
        Args:
            batch_chunks: List of (index, chunk) tuples
            
        Returns:
            List of chunks with embeddings
            
        Raises:
            RuntimeError: If API call fails or response is invalid
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
            
        batch_content = [chunk[1]['content'] for chunk in batch_chunks]
        
        try:
            response = self.client.embeddings.create(
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
        raise ValueError("Repository name cannot be empty")
    if not embedded_chunks:
        raise ValueError("No embedded chunks to save")
        
    embeddings_dir = get_storage_path(base_dir, 'embeddings', repo_name)
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    
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
