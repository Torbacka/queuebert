import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv


class SlackClient:
    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv('OAUTH_TOKEN')
        if not self.bot_token:
            raise ValueError("Slack bot token is missing")

        self.client = WebClient(token=self.bot_token)

    def send_message(self, channel, text):
        """
        Send a simple text message to a Slack channel or user.

        :param channel: Slack channel ID or user ID
        :param text: Message content
        """
        try:
            # Send a message using Slack's chat.postMessage API
            response = self.client.chat_postMessage(
                channel=channel,
                text=text
            )
            print(f"Message sent successfully: {response['message']['text']}")
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")

    def update(self, channel_id, message_ts, blocks):
        try:
            response = self.client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="",
                blocks=blocks
            )
            print("Message updated successfully:", response['message']['text'])
        except SlackApiError as e:
            print(f"Error updating message: {e}")

    def send_message_with_blocks(self, channel, text, blocks):
        """
        Send a message to a Slack channel with blocks (interactive elements like buttons).

        :param channel: Slack channel ID or user ID
        :param text: Message content
        :param blocks: List of block elements to add to the message
        """
        try:
            # Send a message with blocks using Slack's chat.postMessage API
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            print(f"Message sent with blocks: {response['message']['text']}")
        except SlackApiError as e:
            print(f"Error sending message with blocks: {e.response['error']}")
