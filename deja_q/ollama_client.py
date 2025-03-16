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
        thread_content = f"""Original Question:
{question}

Responses:
{chr(10).join(f'- {response}' for response in responses)}"""

        # Construct the prompt
        prompt = f"""Given this Slack thread, extract and summarize the answer to the question. If there is no clear answer, explicitly state that.

{thread_content}

Instructions:
1. Focus ONLY on responses that attempt to answer the question
2. If there are multiple valid answers, combine them into a coherent summary
3. If there is no clear answer in the responses, respond with "No clear answer was provided in the thread."
4. Ignore any follow-up questions or off-topic discussions
5. Be concise but include important technical details

Summary:"""
        
        system_prompt = """You are a precise technical assistant that extracts answers from Slack threads.
Your goal is to find and summarize ONLY the answer to the original question.
If no clear answer exists, you must say so.
Do not include speculation or information not directly related to answering the original question."""
        
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