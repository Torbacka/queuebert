import os

import requests
from flask import current_app
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackClient:
    def __init__(self):
        if os.getenv("ENV") == "production":
            self.host = "https://slack.com"
        else:
            # Wiremock
            self.host = "https://slack.com"
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")


    def get_token(self, auth_code):
        response = requests.post(
            f"{self.host}/api/oauth.v2.access",
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': auth_code,
                'redirect_uri': self.redirect_uri
            }
        )

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Failed to request token for code {auth_code}")

        data = response.json()
        if not data.get("ok"):
            raise Exception(f"Slack error: {data.get('error')}")
        # Save or process the access token and workspace details
        return data['team']['id'], data

    def send_message(self, token, channel, text):
        """
        Send a simple text message to a Slack channel or user.

        :param channel: Slack channel ID or user ID
        :param text: Message content
        """
        try:
            client = WebClient(token=token)
            # Send a message using Slack's chat.postMessage API
            response = client.chat_postMessage(
                channel=channel,
                text=text
            )
            current_app.logger.info(f"Message sent successfully: {response['message']['text']}")
        except SlackApiError as e:
            current_app.logger.info(f"Error sending message: {e.response['error']}")

    def update(self,token, channel_id, message_ts, blocks):
        try:
            client = WebClient(token=token)
            response = client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="",
                blocks=blocks
            )
            current_app.logger.info("Message updated successfully:", response['message']['text'])
        except SlackApiError as e:
            current_app.logger.info(f"Error updating message: {e}")

    def send_message_with_blocks(self, token, channel, text, blocks):
        """
        Send a message to a Slack channel with blocks (interactive elements like buttons).

        :param channel: Slack channel ID or user ID
        :param text: Message content
        :param blocks: List of block elements to add to the message
        """
        try:
            # Send a message with blocks using Slack's chat.postMessage API
            client = WebClient(token=token)
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            current_app.logger.info(f"Message sent with blocks: {response['message']['text']}")
        except SlackApiError as e:
            current_app.logger.info(f"Error sending message with blocks: {e.response['error']}")
