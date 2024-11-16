import pytest

from tests.fixtures.firestore import shared_firestore

from tests.fixtures.app import shared_application


@pytest.mark.integration
def test_missing_oauth_code_should_generate_400_error(shared_application, shared_firestore):
    # Given
    # When
    response = shared_application.post("/oauth/callback")
    # Then
    assert response.status_code == 400