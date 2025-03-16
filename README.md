# Deja Q

Deja Q is a Slack app that helps users find answers to their questions by automatically searching for similar questions that have been asked before. If a similar question is found, Deja Q posts a link to that question in the Slack thread. Optionally, it can also summarize and produce an answer.

## Running the Bot

### Local Development

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables in a `.env` file:
   ```
   SLACK_SIGNING_SECRET=your_signing_secret
   SLACK_BOT_TOKEN=your_bot_token
   ```

3. Start the local Flask server:
   ```bash
   python deja_q/bot.py
   ```
   This will start the server on `localhost:3000`

### Exposing to the Internet

To make your local bot accessible to Slack, you'll need to expose it using ngrok:

1. Sign up for a free ngrok account at https://ngrok.com/signup

2. Install ngrok following the instructions at https://ngrok.com/download

3. Start an ngrok tunnel to your local server:
   ```bash
   ngrok http 3000
   ```

4. Copy the HTTPS URL provided by ngrok (e.g., `https://your-unique-id.ngrok.io`)

5. Update your Slack app's Event Subscriptions URL in the Slack API dashboard to:
   `https://your-unique-id.ngrok.io/slack/events`

Note: The ngrok URL changes each time you restart ngrok unless you have a paid account. Make sure to update your Slack app's Event Subscriptions URL whenever the ngrok URL changes.