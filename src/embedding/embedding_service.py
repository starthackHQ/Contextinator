import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import openai
from ..utils import ProgressTracker
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
            print(f"Warning: Chunk may exceed token limit ({estimated_tokens} estimated tokens)")
            return False
        
        return True
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate embeddings for a list of chunks."""
        if not chunks:
            print("No chunks provided for embedding generation")
            return []
        
        print(f"🚀 Starting embedding generation for {len(chunks)} chunks...")
        print(f"📊 Using model: {OPENAI_EMBEDDING_MODEL}")
        print(f"📦 Batch size: {EMBEDDING_BATCH_SIZE}")
        
        valid_chunks = []
        for i, chunk in enumerate(chunks):
            content = chunk.get('content', '')
            if self._validate_chunk_content(content):
                valid_chunks.append((i, chunk))
            else:
                print(f"⚠️  Skipping invalid chunk at index {i}")
        
        if not valid_chunks:
            raise RuntimeError("No valid chunks found for embedding generation")
        
        print(f"✅ Processing {len(valid_chunks)} valid chunks")
        
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
        print(f"✅ Successfully generated embeddings for {len(embedded_chunks)} chunks")
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


def embed_chunks(repo_path: str, save: bool = False, chunks_data: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Generate embeddings for repository chunks."""
    if chunks_data is None:
        chunks_data = load_chunks(repo_path)
    
    if not chunks_data:
        print("No chunks found to embed")
        return []
    
    embedding_service = EmbeddingService()
    embedded_chunks = embedding_service.generate_embeddings(chunks_data)
    
    if save:
        save_embeddings(embedded_chunks, repo_path)
    
    return embedded_chunks


def load_chunks(repo_path: str) -> List[Dict[str, Any]]:
    """Load chunks from disk."""
    chunks_file = Path(repo_path) / CHUNKS_DIR / 'chunks.json'
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
    
    print(f"📂 Loading chunks from {chunks_file}")
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        chunks = data
    else:
        chunks = data.get('chunks', [])
    
    print(f"📊 Loaded {len(chunks)} chunks")
    return chunks


def save_embeddings(embedded_chunks: List[Dict[str, Any]], repo_path: str):
    """Save embeddings to disk."""
    from ..config import EMBEDDINGS_DIR
    
    embeddings_dir = Path(repo_path) / EMBEDDINGS_DIR
    embeddings_dir.mkdir(exist_ok=True)
    
    output_file = embeddings_dir / 'embeddings.json'
    
    data = {
        'embeddings': embedded_chunks,
        'model': OPENAI_EMBEDDING_MODEL,
        'total_chunks': len(embedded_chunks)
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Embeddings saved to {output_file}")


def load_embeddings(repo_path: str) -> List[Dict[str, Any]]:
    """Load embeddings from disk."""
    from ..config import EMBEDDINGS_DIR
    
    embeddings_file = Path(repo_path) / EMBEDDINGS_DIR / 'embeddings.json'
    
    if not embeddings_file.exists():
        raise FileNotFoundError(f"Embeddings file not found: {embeddings_file}")
    
    with open(embeddings_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return data
    return data.get('embeddings', [])
