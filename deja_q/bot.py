import os
import logging
from flask import Flask, request, jsonify
from slackeventsapi import SlackEventAdapter
from slack_sdk import WebClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
PROTOTYPE_CHANNEL_NAME = 'prototype'

# Initialize Flask app
app = Flask(__name__)

# Initialize Slack client and Events API adapter
client = WebClient(token=SLACK_BOT_TOKEN)
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Event listener for messages
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    
    # Ignore messages from bots and apps to prevent loops
    if (message.get("subtype") is None and  # No subtype (regular message)
            not message.get("bot_id") and    # Not from a bot
            not message.get("app_id") and    # Not from an app
            message.get("user")):            # Has a real user
        try:
            # Get channel info
            channel_info = client.conversations_info(channel=message["channel"])
            channel_name = channel_info["channel"]["name"]
            
            # Check if this is the prototype channel
            if channel_name == PROTOTYPE_CHANNEL_NAME:
                # Reply to the message
                response = client.chat_postMessage(
                    channel=message["channel"],
                    thread_ts=message.get("ts"),
                    text="If I had access to a vector DB of previously posted messages, and an LLM, I would have helped you with an answer"
                )
                logging.info(f"Sent response to message: {message['text']}")
        except Exception as e:
            logging.error(f"Error handling message: {str(e)}")
        
        logging.info(f"Received message: {message['text']} from {message['user']} in {message['channel']}")

# Health check route
@app.route("/", methods=["GET"])
def health_check():
    return "Slack Bot is running!", 200

# Run the app
if __name__ == "__main__":
    app.run(port=3000)
