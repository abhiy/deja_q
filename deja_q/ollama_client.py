import requests
import logging
from typing import Optional, List, Dict

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        """Initialize Ollama client.
        
        Args:
            base_url: The base URL for Ollama API
            model: The model to use for generation
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        
        # Configure logging format
        self.logger = logging.getLogger(__name__)
        
    def _log_interaction(self, thread_id: str, prompts: Dict[str, str], response: str) -> None:
        """Log the interaction with the model in a consistent format.
        
        Args:
            thread_id: Identifier for the thread being processed
            prompts: Dictionary containing system and user prompts
            response: The model's response
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"Thread: {thread_id}")
        self.logger.info(f"{'='*80}")
        self.logger.info("System Prompt:")
        self.logger.info(f"{prompts.get('system', 'No system prompt found')}")
        self.logger.info("\nUser Prompt:")
        self.logger.info(f"{prompts.get('prompt', 'No user prompt found')}")
        self.logger.info("\nModel Response:")
        self.logger.info(f"{response}")
        self.logger.info(f"{'='*80}\n")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response using Ollama.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to guide the model's behavior
        
        Returns:
            The generated response
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            # Construct the payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()["response"]
            
        except Exception as e:
            logging.error(f"Error generating response from Ollama: {str(e)}")
            raise

    def prepare_prompt(self, messages: List[str]) -> Dict[str, str]:
        """Prepare the prompt for thread summarization.
        
        Args:
            messages: List of messages in the thread, where messages[0] is the question
            
        Returns:
            Dict containing 'prompt' and 'system' keys with the formatted prompts
        """
        if len(messages) < 2:
            return {
                "prompt": "",
                "system": "N/A - Empty thread"
            }

        # Separate the question from the responses
        question = messages[0]
        responses = messages[1:]
        
        # Format the thread content
        thread_content = f"""Question: {question}

Thread Messages:
{chr(10).join(f'- {response}' for response in responses)}"""

        # Construct the prompt
        prompt = f"""Extract only information that is explicitly mentioned in this thread.

{thread_content}

Instructions:
- Provide a single-line summary using ONLY information stated in the thread messages
- Include specific technical details that were mentioned
- Do not add external knowledge or make assumptions
- If no relevant information exists, say "No relevant information found"

One-line summary of what was mentioned:"""
        
        system_prompt = """You are a precise information extractor that only reports what was explicitly stated in thread messages.
Restrict yourself to ONLY information that appears in the messages - do not add external knowledge or make assumptions.
Focus on being accurate to what was actually said rather than being comprehensive.
Always respond with a single line of text containing only information from the thread."""
        
        return {
            "prompt": prompt,
            "system": system_prompt
        }

    def summarize_thread(self, messages: List[str], thread_id: Optional[str] = None) -> str:
        """Summarize a thread of messages.
        
        Args:
            messages: List of messages in the thread, where messages[0] is the question
            thread_id: Optional identifier for the thread (e.g. Slack thread timestamp)
        
        Returns:
            A summary of the answer(s) found in the thread
        """
        try:
            if len(messages) < 2:
                return "No answers found in the thread."

            # Get the prepared prompts
            prompts = self.prepare_prompt(messages)
            
            # Generate the summary
            response = self.generate(prompts["prompt"], prompts["system"])
            
            # Log the interaction
            thread_identifier = thread_id or messages[0][:50] + "..."
            self._log_interaction(thread_identifier, prompts, response)
            
            return response
            
        except Exception as e:
            logging.error(f"Error summarizing thread: {str(e)}")
            raise 