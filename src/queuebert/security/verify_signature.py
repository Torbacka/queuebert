# Set your Slack signing secret as an environment variable for security
import hashlib
import hmac
import os
import time
from functools import wraps

from flask import request, abort


def verify_slack_signature(slack_signing_secret=os.getenv("SIGNING_SECRET")):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = request.headers.get("X-Slack-Request-Timestamp")
            slack_signature = request.headers.get("X-Slack-Signature")
            if slack_signature is None:
                return abort(400, "Header X-Slack-Signature is mandatory")
            if not timestamp.isnumeric() or abs(time.time() - int(timestamp)) > 60 * 5:
                return abort(400, "Request is too old")

            sig_basestring = f"v0:{timestamp}:{request.get_data(as_text=True)}"

            my_signature = "v0=" + hmac.new(
                slack_signing_secret.encode(),
                sig_basestring.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(my_signature, slack_signature):
                return abort(400, "Invalid Slack signature")

            return func(*args, **kwargs)
        return wrapper
    return decorator
