import pytest

from src.app import app

@pytest.fixture(scope="session")
def shared_application():
    app.config['TESTING'] = True  # Enable Flask's testing mode
    with app.test_client() as client:
        yield client