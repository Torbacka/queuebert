import json
import os

from google.cloud import firestore


class TokenRepository:

    def __init__(self):
        if os.getenv("ENV") != "production":
            os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
        self.token_collection = firestore.Client(database="queuebert-firestore").collection("tokens")

    def store_token(self, team, token_document):
        result = self.token_collection.document(team).set(token_document, merge=True)
        print(f"Store team token result {json.dumps(result)}")
        if not result.transform_results:
            raise Exception(f"Fail to store token inside firestore for team {team}")


    def get_token(self, team):
        token_document = self.token_collection.document(team).get().to_dict()
        if token_document is None:
            raise Exception(f"Token not found inside firestore for team {team}")
        return token_document["access_token"]