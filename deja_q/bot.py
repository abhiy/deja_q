import os
import logging
from flask import Flask
from slackeventsapi import SlackEventAdapter
from dotenv import load_dotenv
from deja_q.vector_store import MessageVectorStore
from deja_q.message_handler import MessageHandler

# Load environment variables
load_dotenv()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
PROTOTYPE_CHANNEL_NAME = 'prototype'

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)
    
    # Initialize vector store and message handler
    vector_store = MessageVectorStore(PROTOTYPE_CHANNEL_NAME)
    message_handler = MessageHandler(vector_store)

    # Initialize Slack Events API adapter
    slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

    try:
        vector_store.initialize()
        logging.info("Vector store initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing vector store: {str(e)}")
        # Continue running even if vector store fails to initialize
        # This way we can still send the placeholder message

    @slack_events_adapter.on("message")
    def handle_message(event_data):
        """Route incoming messages to the message handler."""
        message_handler.handle_message(event_data)

    @app.route("/", methods=["GET"])
    def health_check():
        return "Slack Bot is running!", 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=3000)
