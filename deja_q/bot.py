import os
import inspect
import slack_sdk
from slack_sdk.rtm_v2 import RTMClient
from slack_sdk.web import WebClient
from dotenv import load_dotenv
load_dotenv() 

# Make sure we have the token
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
if not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN environment variable is not set")

# Create RTM client
rtm = RTMClient(token=SLACK_BOT_TOKEN)

# Create a separate web client for sending messages
web_client = WebClient(token=SLACK_BOT_TOKEN)

# Define the message handler separately first
@rtm.on("message")
def handle_message(client, event):
    """Handle incoming message events."""
    print(f"Received message: {event}")
    # Additional message handling logic can go here

# Debug: Print function signature information
print(f"Function name: {handle_message.__name__}")
print(f"Function signature: {inspect.signature(handle_message)}")
print(f"Function parameters: {list(inspect.signature(handle_message).parameters.keys())}")

if __name__ == "__main__":
    print("Starting RTM client...")
    rtm.start()
