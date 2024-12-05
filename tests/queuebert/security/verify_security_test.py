import hashlib
import hmac
import os
import time
from unittest import mock
from unittest.mock import MagicMock

import pytest

from src.queuebert.security.verify_signature import verify_slack_signature

@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with mock.patch.dict(os.environ, {"SIGNING_SECRET": "mock_secret"}):
        yield


def generate_slack_signature(secret, timestamp, body):
    sig_basestring = f"v0:{timestamp}:{body}"
    return "v0=" + hmac.new(secret.encode(), sig_basestring.encode(), hashlib.sha256).hexdigest()

@mock.patch.dict(os.environ, {"SIGNING_SECRET": "mock_secret"})
def test_valid_signature(mocker):
    """Test the decorator with a valid Slack signature."""
    # Given
    mock_func = MagicMock(return_value="decorated_function_called")
    decorated_func = verify_slack_signature(os.getenv("SIGNING_SECRET"))
    timestamp = str(int(time.time()))
    body = '{"text": "Hello, world!"}'
    slack_signature = generate_slack_signature(os.getenv("SIGNING_SECRET"), timestamp, body)
    mock_request = mocker.patch("src.queuebert.security.verify_signature.request", mock_func)
    mock_request.headers = {
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": slack_signature,
    }
    mock_request.get_data.return_value = body

    # When
    result = decorated_func(mock_func)()
    # Then
    mock_func.assert_called_once()
    assert result == "decorated_function_called"


def test_invalid_signature(mocker):
    """Test the decorator with an invalid Slack signature."""
    # Given
    mock_func = MagicMock()
    decorated_func = verify_slack_signature(os.getenv("SIGNING_SECRET"))
    timestamp = str(int(time.time()))
    body = '{"text": "Hello, world!"}'
    invalid_signature = "v0=invalid_signature"
    mock_request = mocker.patch("src.queuebert.security.verify_signature.request", mock_func)
    mock_request.headers = {
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": invalid_signature,
    }
    mock_request.get_data.return_value = body

    # When
    with pytest.raises(Exception) as exc_info:
        decorated_func(mock_func)()    # Then
    mock_func.assert_not_called()
    assert exc_info.value.code == 400


def test_request_too_old(mocker):
    """Test the decorator with an old timestamp."""
    # Given
    mock_func = MagicMock()
    decorated_func = verify_slack_signature(os.getenv("SIGNING_SECRET"))
    old_timestamp = str(int(time.time()) - (60 * 6))  # 6 minutes old
    body = '{"text": "Hello, world!"}'
    slack_signature = generate_slack_signature(os.getenv("SIGNING_SECRET"), old_timestamp, body)
    mock_request = mocker.patch("src.queuebert.security.verify_signature.request", mock_func)
    mock_request.headers = {
        "X-Slack-Request-Timestamp": old_timestamp,
        "X-Slack-Signature": slack_signature,
    }
    mock_request.get_data.return_value = body

    # When
    with pytest.raises(Exception) as exc_info:
        decorated_func(mock_func)()
    # Then
    mock_func.assert_not_called()
    assert exc_info.value.code == 400


def test_missing_headers(mocker):
    """Test the decorator with missing headers."""
    # Given
    mock_func = MagicMock()
    decorated_func = verify_slack_signature(os.getenv("SIGNING_SECRET"))
    mock_request = mocker.patch("src.queuebert.security.verify_signature.request", mock_func)
    mock_request.headers = {}  # Missing headers
    mock_request.get_data.return_value = '{"text": "Hello, world!"}'

    # When
    with pytest.raises(Exception) as exc_info:
        decorated_func(mock_func)()
    # Then
    mock_func.assert_not_called()
    assert exc_info.value.code == 400  # HTTP 400 Bad Request


def test_invalid_timestamp_format(mocker):
    """Test the decorator with an invalid timestamp format."""
    # Given
    mock_func = MagicMock()
    decorated_func = verify_slack_signature(os.getenv("SIGNING_SECRET"))
    old_timestamp = int(time.time()) - (60 * 6)
    body = '{"text": "Hello, world!"}'
    slack_signature = generate_slack_signature(os.getenv("SIGNING_SECRET"), old_timestamp, body)
    mock_request = mocker.patch("src.queuebert.security.verify_signature.request", mock_func)
    mock_request.headers = {
        "X-Slack-Request-Timestamp": f"old_timestamp",
        "X-Slack-Signature": slack_signature,
    }
    mock_request.get_data.return_value = body

    # When
    with pytest.raises(Exception) as exc_info:
        decorated_func(mock_func)()
    # Then
    mock_func.assert_not_called()
    assert exc_info.value.code == 400


def test_timestamp_to_old(mocker):
    """Test the decorator with an invalid timestamp format."""
    # Given
    mock_func = MagicMock()
    decorated_func = verify_slack_signature(os.getenv("SIGNING_SECRET"))
    invalid_timestamp = "not_a_number"
    body = '{"text": "Hello, world!"}'
    slack_signature = generate_slack_signature(os.getenv("SIGNING_SECRET"), invalid_timestamp, body)
    mock_request = mocker.patch("src.queuebert.security.verify_signature.request", mock_func)
    mock_request.headers = {
        "X-Slack-Request-Timestamp": invalid_timestamp,
        "X-Slack-Signature": slack_signature,
    }
    mock_request.get_data.return_value = body

    # When
    with pytest.raises(Exception) as exc_info:
        decorated_func(mock_func)()
    # Then
    mock_func.assert_not_called()
    assert exc_info.value.code == 400
