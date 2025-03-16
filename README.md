# Deja Q

Deja Q is a Slack app that helps users find answers to their questions by automatically searching for similar questions that have been asked before. If a similar question is found, Deja Q posts a link to that question in the Slack thread and provides a summary of the previous answer using Ollama.

## Prerequisites

1. Slack App with appropriate permissions
2. Ollama installed and running locally (or accessible via URL)
3. Python 3.11 or higher

## Configuration

1. Set up your environment variables in a `.env` file:
   ```
   SLACK_SIGNING_SECRET=your_signing_secret
   SLACK_BOT_TOKEN=your_bot_token
   OLLAMA_BASE_URL=http://localhost:11434  # Optional, defaults to http://localhost:11434
   OLLAMA_MODEL=mistral                    # Optional, defaults to mistral
   ```

2. Make sure Ollama is running and the specified model is available:
   ```bash
   # Pull the model if you haven't already
   ollama pull mistral
   
   # Start Ollama (if not already running)
   ollama serve
   ```

## Running the Bot

### Local Development

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Start the local Flask server:
   ```bash
   python -m deja_q.bot
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

5. Update your Slack app settings:
   - Go to your Slack App settings in the Slack API dashboard
   - Navigate to "Event Subscriptions"
   - Enable Events if not already enabled
   - Paste your full URL with `/slack/events` into the "Request URL" field

Note: The ngrok URL changes each time you restart ngrok unless you have a paid account. Make sure to update your Slack app's Event Subscriptions URL whenever the ngrok URL changes.

## Features

1. **Similar Question Detection**: Uses sentence transformers to find semantically similar questions
2. **Thread Summarization**: Uses Ollama to generate concise summaries of previous answer threads
3. **Automatic Learning**: Adds new questions to its knowledge base as they are asked