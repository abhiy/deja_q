import os
import logging
from flask import Flask, request, jsonify
from slackeventsapi import SlackEventAdapter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Initialize Flask app
app = Flask(__name__)

# Initialize Slack Events API adapter
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Event listener for messages
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    
    # Ignore messages from bots to prevent loops
    if message.get("subtype") is None:
        logging.info(f"Received message: {message['text']} from {message['user']} in {message['channel']}")

# Health check route
@app.route("/", methods=["GET"])
def health_check():
    return "Slack Bot is running!", 200

# Run the app
if __name__ == "__main__":
    app.run(port=3000)
