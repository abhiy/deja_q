import pytest
from deja_q.vector_store import MessageVectorStore
import numpy as np

class TestMessageVectorStore:
    @pytest.fixture
    def mock_messages(self):
        """Sample messages for testing."""
        return [
            {
                "text": "How do I configure my AWS credentials?",
                "ts": "1234567890.123456",
                "user": "U123456",
                "permalink": "https://slack.com/1"
            },
            {
                "text": "What's the best way to set up AWS credentials on my machine?",
                "ts": "1234567891.123456",
                "user": "U123457",
                "permalink": "https://slack.com/2"
            },
            {
                "text": "How do I deploy a Flask application to Heroku?",
                "ts": "1234567892.123456",
                "user": "U123458",
                "permalink": "https://slack.com/3"
            }
        ]

    @pytest.fixture
    def vector_store(self, monkeypatch, mock_messages):
        """Initialize a vector store with mock messages."""
        def mock_fetch_channel_history(self):
            self.messages = mock_messages

        # Patch the fetch_channel_history method
        monkeypatch.setattr(MessageVectorStore, 'fetch_channel_history', mock_fetch_channel_history)
        
        # Create and initialize vector store
        store = MessageVectorStore('test-channel')
        store.initialize()
        return store

    def test_initialization(self, vector_store, mock_messages):
        """Test that the vector store initializes correctly."""
        assert len(vector_store.messages) == len(mock_messages)
        assert vector_store.embeddings is not None
        assert len(vector_store.embeddings) == len(mock_messages)

    def test_similar_messages_found(self, vector_store):
        """Test that similar messages are found correctly."""
        # Test query similar to first two messages (about AWS credentials)
        query = "How can I set up my AWS credentials properly?"
        results = vector_store.find_similar_messages(query, threshold=0.5)
        
        # Should find at least 2 similar messages (the AWS-related ones)
        assert len(results) >= 2
        
        # Check that similarities are sorted in descending order
        similarities = [result["similarity"] for result in results]
        assert similarities == sorted(similarities, reverse=True)

    def test_no_similar_messages(self, vector_store):
        """Test that unrelated queries don't return false positives."""
        query = "What's the current price of Bitcoin?"
        results = vector_store.find_similar_messages(query, threshold=0.8)
        
        # Should find no similar messages with high threshold
        assert len(results) == 0

    def test_similarity_threshold(self, vector_store):
        """Test that similarity threshold is respected."""
        query = "How do I configure AWS?"
        
        # With high threshold
        high_threshold_results = vector_store.find_similar_messages(query, threshold=0.9)
        
        # With lower threshold
        low_threshold_results = vector_store.find_similar_messages(query, threshold=0.5)
        
        # Should find more results with lower threshold
        assert len(low_threshold_results) >= len(high_threshold_results)

    def test_embeddings_shape(self, vector_store, mock_messages):
        """Test that embeddings have correct shape."""
        # Get dimensionality of a single embedding
        test_text = "test message"
        test_embedding = vector_store.model.encode([test_text])[0]
        embedding_dim = len(test_embedding)
        
        # Check that all embeddings have correct shape
        assert vector_store.embeddings.shape == (len(mock_messages), embedding_dim)

    def test_new_message_similarity(self, vector_store):
        """Test similarity with a new message."""
        # Original message in mock data: "How do I configure my AWS credentials?"
        new_message = "What's the process for setting up AWS credential configuration?"
        
        results = vector_store.find_similar_messages(new_message, threshold=0.7)
        
        # Should find similar AWS-related messages
        assert len(results) > 0
        # First result should have high similarity
        assert results[0]["similarity"] > 0.7 