import os
import logging
from dotenv import load_dotenv
import slack_sdk
from slack_sdk.errors import SlackApiError

load_dotenv()  # Load environment variables from .env file

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
client = slack_sdk.WebClient(token=SLACK_BOT_TOKEN)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # This line ensures the logger uses INFO level

def post_message(channel, text):
    try:
        logger.debug(f"Attempting to post message to channel: {channel}")
        
        # Log before fetching the list of channels
        logger.debug("Fetching the list of channels...")
        response = client.conversations_list(types="public_channel,private_channel")
        logger.debug("Fetched the list of channels.")
        
        channels = response['channels']
        logger.debug(f"Fetched channels: {channels}")
        
        # Find the channel ID by name
        channel_id = next((ch['id'] for ch in channels if ch['name'] == channel.strip('#')), None)
        logger.debug(f"Channel ID for {channel}: {channel_id}")
        
        if not channel_id:
            logger.error(f"Error: Channel {channel} not found or bot is not a member of the channel.")
            return
        
        # Post the message using the channel ID
        response = client.chat_postMessage(channel=channel_id, text=text)
        logger.info(f"Message posted successfully: {response}")
        return response
    except SlackApiError as e:
        logger.error(f"Error: {e.response['error']}")
        logger.error(f"Full error response: {e.response}")

if __name__ == "__main__":
    test_channel = "prototype"  # Change to your Slack channel
    post_message(test_channel, "Hello! Deja Q is online.")
