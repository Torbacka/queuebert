import pytest

from src.queuebert.service.database.TokenRepository import TokenRepository
from tests.fixtures.app import shared_application
from tests.fixtures.firestore import shared_firestore
from tests.fixtures.wiremock import slack_wiremock


@pytest.mark.integration
def test_missing_oauth_code_should_generate_400_error(shared_application):
    # When
    response = shared_application.post("/oauth/callback")
    # Then
    assert response.status_code == 400

@pytest.mark.integration
def test_storing_successful_token(shared_application, slack_wiremock, shared_firestore):
    _, wiremock_port = slack_wiremock
    response = shared_application.get("/oauth/callback?code=cooltoken")

    token_repository = TokenRepository()
    assert response.status_code == 200
    assert token_repository.get_token("slack-bots") == 'secret_test_token'
