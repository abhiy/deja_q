import pytest
from unittest.mock import Mock, patch
from deja_q.ollama_client import OllamaClient

class TestOllamaClient:
    @pytest.fixture
    def ollama_client(self):
        return OllamaClient(model="llama3.2")

    @pytest.fixture
    def mock_response(self):
        """Mock response from Ollama API"""
        mock = Mock()
        mock.json.return_value = {"response": "Mocked summary response"}
        mock.raise_for_status.return_value = None
        return mock

    def log_test_details(self, name, payload, response):
        """Helper to log test details in a consistent format"""
        print(f"\n{'='*80}")
        print(f"Test: {name}")
        print(f"{'='*80}")
        print("System Prompt:")
        print(f"{payload.get('system', 'No system prompt found')}")
        print("\nUser Prompt:")
        print(f"{payload.get('prompt', 'No user prompt found')}")
        print("\nModel Response:")
        print(f"{response}")
        print(f"{'='*80}\n")

    def test_single_clear_answer(self, ollama_client, mock_response):
        """Test summarization with a single clear answer."""
        messages = [
            "How do I install Python on macOS?",  # Question
            "You can install Python using Homebrew. Just run: brew install python",  # Clear answer
            "Thanks, that worked!",  # Confirmation
        ]

        with patch('requests.post', return_value=mock_response) as mock_post:
            summary = ollama_client.summarize_thread(messages)
            
            call_args = mock_post.call_args
            payload = call_args[1]['json']
            
            self.log_test_details("Single Clear Answer", payload, summary)
            
            # Original assertions
            assert "Original Question:" in payload['prompt']
            assert messages[0] in payload['prompt']
            assert messages[1] in payload['prompt']
            assert "Instructions:" in payload['prompt']
            assert "extract" in payload['system'].lower()
            assert "answer" in payload['system'].lower()

    def test_multiple_answers(self, ollama_client, mock_response):
        """Test summarization with multiple valid answers."""
        messages = [
            "What's the best way to learn Python?",
            "I recommend starting with Python's official tutorial",
            "Codecademy has a great Python course",
            "I learned from 'Automate the Boring Stuff with Python'",
            "The official tutorial is too dry for beginners",
        ]

        with patch('requests.post', return_value=mock_response) as mock_post:
            summary = ollama_client.summarize_thread(messages)
            
            payload = mock_post.call_args[1]['json']
            self.log_test_details("Multiple Answers", payload, summary)
            
            for msg in messages[1:]:
                assert msg in payload['prompt']

    def test_no_clear_answer(self, ollama_client, mock_response):
        """Test handling of threads with no clear answer."""
        messages = [
            "How do I fix this Python error?",
            "Can you share more details about the error?",
            "What version of Python are you using?",
            "I'm having a similar issue",
        ]

        with patch('requests.post', return_value=mock_response) as mock_post:
            summary = ollama_client.summarize_thread(messages)
            
            payload = mock_post.call_args[1]['json']
            self.log_test_details("No Clear Answer", payload, summary)
            
            assert "no clear answer" in payload['system'].lower()

    def test_empty_thread(self, ollama_client):
        """Test handling of empty threads."""
        messages = ["How do I do this?"]  # Only question, no responses
        
        summary = ollama_client.summarize_thread(messages)
        self.log_test_details("Empty Thread", {"system": "N/A - Empty thread"}, summary)
        
        assert summary == "No answers found in the thread."

    def test_off_topic_responses(self, ollama_client, mock_response):
        """Test handling of threads with off-topic responses."""
        messages = [
            "How do I set up a PostgreSQL database?",
            "I'm having lunch",
            "Anyone watching the game tonight?",
            "You need to install PostgreSQL first, then run initdb",
            "Great weather today!",
        ]

        with patch('requests.post', return_value=mock_response) as mock_post:
            summary = ollama_client.summarize_thread(messages)
            
            payload = mock_post.call_args[1]['json']
            self.log_test_details("Off-topic Responses", payload, summary)
            
            assert "Focus ONLY on responses that attempt to answer" in payload['prompt']

    def test_actual_llama_response(self, ollama_client):
        """Test with actual Llama model (not mocked) to see real responses."""
        # Technical question test
        messages = [
            "How do I install Python packages?",
            "You can use pip install package_name",
            "For virtual environments, use python -m venv first",
            "pip is the standard package installer",
        ]

        # Get the prompt that would be sent to the model
        prompt_payload = ollama_client.prepare_prompt(messages)
        summary = ollama_client.summarize_thread(messages)
        self.log_test_details("Actual Llama - Technical Question", prompt_payload, summary)
        
        # Subjective question test
        unclear_messages = [
            "What's the best programming language?",
            "It depends on what you want to do",
            "Python is popular",
            "I prefer JavaScript",
            "C++ is faster though",
        ]
        
        prompt_payload = ollama_client.prepare_prompt(unclear_messages)
        unclear_summary = ollama_client.summarize_thread(unclear_messages)
        self.log_test_details("Actual Llama - Subjective Question", prompt_payload, unclear_summary)

    @pytest.mark.parametrize("test_case", [
        {
            "name": "Technical answer",
            "messages": [
                "How do I set up Git?",
                "1. Install Git: brew install git",
                "2. Configure: git config --global user.name 'Your Name'",
                "3. Configure: git config --global user.email 'email@example.com'",
            ]
        },
        {
            "name": "Conceptual answer",
            "messages": [
                "What is dependency injection?",
                "It's a design pattern where dependencies are passed in rather than created internally",
                "This makes testing easier because you can mock the dependencies",
                "It's a form of inversion of control",
            ]
        },
        {
            "name": "No clear answer",
            "messages": [
                "What's the ETA for the project?",
                "Have you checked with the PM?",
                "We should discuss this in the next meeting",
                "I'm not sure either",
            ]
        },
    ])
    def test_various_thread_types(self, ollama_client, test_case):
        """Test different types of threads to see how Llama handles them."""
        prompt_payload = ollama_client.prepare_prompt(test_case["messages"])
        summary = ollama_client.summarize_thread(test_case["messages"])
        self.log_test_details(f"Various Thread Types - {test_case['name']}", prompt_payload, summary)

if __name__ == "__main__":
    # For manual testing and debugging
    client = OllamaClient(model="llama3.2")
    
    test_messages = [
        "How do I install Python packages?",
        "You can use pip install package_name",
        "For virtual environments, use python -m venv first",
        "pip is the standard package installer",
    ]
    
    # Get the prompt that would be sent to the model
    prompt_payload = client.prepare_prompt(test_messages)
    summary = client.summarize_thread(test_messages)
    
    print("\nManual Test Results:")
    print("="*80)
    print("System Prompt:")
    print(prompt_payload.get('system', 'No system prompt found'))
    print("\nUser Prompt:")
    print(prompt_payload.get('prompt', 'No user prompt found'))
    print("\nModel Response:")
    print(summary)
    print("="*80) 