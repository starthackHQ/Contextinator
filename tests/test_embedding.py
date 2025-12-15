"""Tests for embedding functionality."""
import pytest
from contextinator.embedding.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Test embedding service functionality."""
    
    def test_initialization(self):
        """Test EmbeddingService initialization."""
        service = EmbeddingService()
        
        assert service is not None
        # Service should have a client after initialization
        assert hasattr(service, 'client')
    
    def test_service_has_generate_embeddings(self):
        """Test that service has generate_embeddings method."""
        service = EmbeddingService()
        
        assert hasattr(service, 'generate_embeddings')
