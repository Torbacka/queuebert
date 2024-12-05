import os

from google.cloud import firestore


class TokenRepository:

    def __init__(self):
        if os.getenv("ENV") != "PROD":
            os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
        self.token_collection = firestore.Client().collection("tokens")

    def store_token(self, team, token_document):
        self.token_collection.document(team).set(token_document)

    def get_token(self, team):
        token_document = self.token_collection.document(team).get().to_dict()
        if token_document is None:
            raise Exception(f"Token not found inside firestore for team {team}")
        return token_document["access_token"]