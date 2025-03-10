import os
from dotenv import load_dotenv
import slack_sdk
from slack_sdk.errors import SlackApiError

load_dotenv()  # Load environment variables from .env file

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
client = slack_sdk.WebClient(token=SLACK_BOT_TOKEN)

def post_message(channel, text):
    try:
        response = client.chat_postMessage(channel=channel, text=text)
        return response
    except SlackApiError as e:
        print(f"Error: {e.response['error']}")

if __name__ == "__main__":
    test_channel = "#general"  # Change to your Slack channel
    post_message(test_channel, "Hello! Deja Q is online.")
