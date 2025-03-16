import os
import logging
from flask import Flask, request
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Track processed message IDs to prevent duplicates
processed_messages = set()

def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)
    
    # Initialize vector store and message handler
    vector_store = MessageVectorStore(PROTOTYPE_CHANNEL_NAME)
    message_handler = MessageHandler(vector_store)

    # Initialize Slack Events API adapter with retry disabled
    slack_events_adapter = SlackEventAdapter(
        SLACK_SIGNING_SECRET,
        "/slack/events",
        app
    )

    try:
        vector_store.initialize()
        logger.info("Vector store initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        # Continue running even if vector store fails to initialize
        # This way we can still send the placeholder message

    @slack_events_adapter.on("message")
    def handle_message(event_data):
        """Route incoming messages to the message handler."""
        # Log the raw event data
        logger.info(f"\n{'='*40} Received Slack Event {'='*40}")
        logger.info(f"Event Type: {event_data.get('type', 'No type')}")
        logger.info(f"Event ID: {event_data.get('event_id', 'No event_id')}")
        logger.info(f"Event Time: {event_data.get('event_time', 'No event_time')}")
        
        # Check if this is a retry
        retry_num = request.headers.get('X-Slack-Retry-Num')
        if retry_num:
            logger.info(f"Received retry attempt #{retry_num} - Ignoring")
            return "", 200
            
        # Get the message from the event
        event = event_data.get("event", {})
        message_subtype = event.get("subtype")
        
        # Check for message_changed events
        if message_subtype == "message_changed":
            logger.info("Ignoring message_changed event")
            return "", 200
            
        # Get unique message identifier
        client_msg_id = event.get("client_msg_id")
        message_ts = event.get("ts")
        message_id = client_msg_id or message_ts
        
        # Check if we've already processed this message
        if message_id in processed_messages:
            logger.info(f"Message {message_id} already processed - Ignoring")
            return "", 200
            
        # Add to processed messages
        if message_id:
            processed_messages.add(message_id)
            # Prevent set from growing indefinitely (keep last 1000 messages)
            if len(processed_messages) > 1000:
                processed_messages.pop()
        
        # Process the message
        message_handler.handle_message(event_data)
        
        logger.info(f"{'='*90}\n")
        return "", 200

    @app.route("/", methods=["GET"])
    def health_check():
        return "Slack Bot is running!", 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=3000)
