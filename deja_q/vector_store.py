import os
import logging
from typing import List, Dict
from slack_sdk import WebClient
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MessageVectorStore:
    def __init__(self, channel_name: str):
        self.channel_name = channel_name
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.messages: List[Dict] = []
        self.embeddings = None

    def fetch_channel_history(self) -> None:
        """Fetch all messages from the specified channel."""
        try:
            # First get the channel ID
            channel_info = self.client.conversations_list()
            channel_id = None
            for channel in channel_info["channels"]:
                if channel["name"] == self.channel_name:
                    channel_id = channel["id"]
                    break

            if not channel_id:
                raise ValueError(f"Channel {self.channel_name} not found")

            # Fetch channel history
            result = self.client.conversations_history(channel=channel_id)
            self.messages = [
                {
                    "text": msg["text"],
                    "ts": msg["ts"],
                    "permalink": self._get_permalink(channel_id, msg["ts"]),
                    "user": msg.get("user")
                }
                for msg in result["messages"]
                if not msg.get("bot_id") and not msg.get("app_id")  # Filter out bot messages
            ]

        except Exception as e:
            logging.error(f"Error fetching channel history: {str(e)}")
            raise

    def _get_permalink(self, channel_id: str, message_ts: str) -> str:
        """Get permalink for a message."""
        try:
            result = self.client.chat_getPermalink(
                channel=channel_id,
                message_ts=message_ts
            )
            return result["permalink"]
        except Exception as e:
            logging.error(f"Error getting permalink: {str(e)}")
            return ""

    def create_embeddings(self) -> None:
        """Create embeddings for all messages."""
        if not self.messages:
            logging.warning("No messages to create embeddings for")
            return

        try:
            texts = [msg["text"] for msg in self.messages]
            embeddings = self.model.encode(texts)
            self.embeddings = np.array(embeddings)
            logging.info(f"Created embeddings with shape {self.embeddings.shape}")
        except Exception as e:
            logging.error(f"Error creating embeddings: {str(e)}")
            raise

    def add_message(self, message: dict, channel_id: str) -> None:
        """Add a new message to the vector store and update embeddings."""
        try:
            # Create message object
            message_obj = {
                "text": message["text"],
                "ts": message["ts"],
                "permalink": self._get_permalink(channel_id, message["ts"]),
                "user": message.get("user")
            }
            
            # Add to messages list
            self.messages.append(message_obj)
            
            # Create embedding for new message
            new_embedding = self.model.encode([message["text"]])[0]
            
            # Update embeddings array
            if self.embeddings is None:
                self.embeddings = np.array([new_embedding])
            else:
                self.embeddings = np.vstack([self.embeddings, new_embedding])
            
            logging.info(f"Added new message to vector store. Total messages: {len(self.messages)}")
        except Exception as e:
            logging.error(f"Error adding message to vector store: {str(e)}")
            raise

    def find_similar_messages(self, query: str, threshold: float = 0.8) -> List[Dict]:
        """
        Find messages similar to the query.
        Returns list of messages with similarity score above threshold.
        """
        if self.embeddings is None:
            raise ValueError("No embeddings available. Run create_embeddings first.")

        try:
            query_embedding = self.model.encode([query])[0]
            query_embedding = np.array(query_embedding)
            
            # Calculate cosine similarity
            norm_embeddings = np.linalg.norm(self.embeddings, axis=1)
            norm_query = np.linalg.norm(query_embedding)
            similarities = np.dot(self.embeddings, query_embedding) / (norm_embeddings * norm_query)

            # Get similar messages above threshold
            similar_messages = []
            for i, similarity in enumerate(similarities):
                if similarity > threshold:
                    similar_messages.append({
                        **self.messages[i],
                        "similarity": float(similarity)
                    })

            return sorted(similar_messages, key=lambda x: x["similarity"], reverse=True)
        except Exception as e:
            logging.error(f"Error finding similar messages: {str(e)}")
            raise

    def initialize(self) -> None:
        """Initialize the vector store by fetching messages and creating embeddings."""
        logging.info("Initializing vector store...")
        self.fetch_channel_history()
        logging.info(f"Fetched {len(self.messages)} messages")
        self.create_embeddings()
        logging.info("Created embeddings for all messages")

    def get_thread_messages(self, channel_id: str, thread_ts: str) -> list[str]:
        """Fetch all messages in a thread.
        
        Args:
            channel_id: The channel ID
            thread_ts: The timestamp of the parent message
            
        Returns:
            List of message texts in the thread
        """
        try:
            # Get replies in the thread
            result = self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts
            )
            
            # Extract message texts, excluding bot messages
            messages = [
                msg["text"] for msg in result["messages"]
                if not msg.get("bot_id") and not msg.get("app_id")
            ]
            
            return messages
            
        except Exception as e:
            logging.error(f"Error fetching thread messages: {str(e)}")
            raise 