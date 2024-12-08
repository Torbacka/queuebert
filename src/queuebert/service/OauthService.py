from flask import current_app

from src.queuebert.service.client.SlackClient import SlackClient
from src.queuebert.service.database.TokenRepository import TokenRepository


class OauthService:
    def __init__(self, token_repository=TokenRepository(), slackClient=SlackClient()):
        self.token_repository = token_repository
        self.slackClient = slackClient

    def getAccessToken(self, auth_code):
        # Exchange the authorization code for an access token
        current_app.logger.info(f"Start to make request to get oauth_token")
        team_id, data = self.slackClient.get_token(auth_code)
        self.token_repository.store_token(team_id, data)
