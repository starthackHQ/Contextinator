import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import openai
from ..utils import ProgressTracker, logger
from ..config import (
    OPENAI_EMBEDDING_MODEL, 
    EMBEDDING_BATCH_SIZE, 
    OPENAI_MAX_TOKENS,
    OPENAI_API_KEY,
    CHUNKS_DIR
)


class EmbeddingService:
    """Service for generating embeddings using OpenAI API."""
    
    def __init__(self):
        """Initialize the embedding service."""
        self.client = None
        self._validate_api_key()
        self._initialize_client()
    
    def _validate_api_key(self):
        """Validate that OpenAI API key is available."""
        if not OPENAI_API_KEY:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY in your .env file."
            )
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            self._test_connection()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def _test_connection(self):
        """Test the OpenAI API connection."""
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
        """Validate chunk content for embedding."""
        if not content or not content.strip():
            return False
        
        estimated_tokens = len(content) // 4
        if estimated_tokens > OPENAI_MAX_TOKENS:
            logger.info(f"Warning: Chunk may exceed token limit ({estimated_tokens} estimated tokens)")
            return False
        
        return True
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate embeddings for a list of chunks."""
        if not chunks:
            logger.info("No chunks provided for embedding generation")
            return []
        
        logger.info(f"🚀 Starting embedding generation for {len(chunks)} chunks...")
        logger.info(f"📊 Using model: {OPENAI_EMBEDDING_MODEL}")
        logger.info(f"📦 Batch size: {EMBEDDING_BATCH_SIZE}")
        
        valid_chunks = []
        for i, chunk in enumerate(chunks):
            content = chunk.get('content', '')
            if self._validate_chunk_content(content):
                valid_chunks.append((i, chunk))
            else:
                logger.info(f"⚠️  Skipping invalid chunk at index {i}")
        
        if not valid_chunks:
            raise RuntimeError("No valid chunks found for embedding generation")
        
        logger.info(f"✅ Processing {len(valid_chunks)} valid chunks")
        
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
    
    def _generate_batch_embeddings(self, batch_chunks: List[tuple]) -> List[Dict[str, Any]]:
        """Generate embeddings for a batch of chunks."""
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


def embed_chunks(base_dir: str, repo_name: str, save: bool = False, chunks_data: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Generate embeddings for repository chunks.
    
    Args:
        base_dir: Base directory containing .chunks folder
        repo_name: Repository name for isolation
        save: Whether to save embeddings to disk
        chunks_data: Optional pre-loaded chunks data
    
    Returns:
        List of embedded chunks
    """
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


def load_chunks(base_dir: str, repo_name: str) -> List[Dict[str, Any]]:
    """
    Load chunks from repository-specific directory.
    
    Args:
        base_dir: Base directory containing .chunks folder
        repo_name: Repository name for isolation
    
    Returns:
        List of chunks
    """
    from ..config import get_storage_path
    
    chunks_file = get_storage_path(base_dir, 'chunks', repo_name) / 'chunks.json'
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
    
    logger.info(f"📂 Loading chunks from {chunks_file}")
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        chunks = data
    else:
        chunks = data.get('chunks', [])
    
    logger.info(f"📊 Loaded {len(chunks)} chunks")
    return chunks


def save_embeddings(embedded_chunks: List[Dict[str, Any]], base_dir: str, repo_name: str):
    """
    Save embeddings to repository-specific directory.
    
    Args:
        embedded_chunks: List of embedded chunks
        base_dir: Base directory
        repo_name: Repository name for isolation
    """
    from ..config import get_storage_path
    
    embeddings_dir = get_storage_path(base_dir, 'embeddings', repo_name)
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = embeddings_dir / 'embeddings.json'
    
    data = {
        'embeddings': embedded_chunks,
        'model': OPENAI_EMBEDDING_MODEL,
        'total_chunks': len(embedded_chunks),
        'repository': repo_name
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 Embeddings saved to {output_file}")


def load_embeddings(base_dir: str, repo_name: str) -> List[Dict[str, Any]]:
    """
    Load embeddings from repository-specific directory.
    
    Args:
        base_dir: Base directory containing .embeddings folder
        repo_name: Repository name for isolation
    
    Returns:
        List of embeddings
    """
    from ..config import get_storage_path
    
    embeddings_file = get_storage_path(base_dir, 'embeddings', repo_name) / 'embeddings.json'
    
    if not embeddings_file.exists():
        raise FileNotFoundError(f"Embeddings file not found: {embeddings_file}")
    
    logger.info(f"📂 Loading embeddings from {embeddings_file}")
    
    with open(embeddings_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return data
    return data.get('embeddings', [])
