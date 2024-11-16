import os

import requests

from src.queuebert.service.database.TokenRepository import TokenRepository


class OauthService:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.token_repository = TokenRepository()

    def getAccessToken(self, auth_code):
        # Exchange the authorization code for an access token
        response = requests.post(
            'https://slack.com/api/oauth.v2.access',
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': auth_code,
                'redirect_uri': self.redirect_uri
            }
        )

        # Check if the request was successful
        if response.status_code != 200:
            return "Failed to retrieve access token", 500

        data = response.json()
        if not data.get("ok"):
            return f"Slack error: {data.get('error')}", 500

        # Save or process the access token and workspace details
        team_name = data['team']['name']
        self.token_repository.store_token(team_name, data)