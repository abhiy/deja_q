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

    def summarize_thread(self, messages: List[str]) -> str:
        """Summarize a thread of messages.
        
        Args:
            messages: List of messages in the thread, where messages[0] is the question
        
        Returns:
            A summary of the answer(s) found in the thread
        """
        try:
            if len(messages) < 2:
                return "No answers found in the thread."

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
            
            return self.generate(prompt, system_prompt)
            
        except Exception as e:
            logging.error(f"Error summarizing thread: {str(e)}")
            raise 