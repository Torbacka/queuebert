import logging
import os

from dotenv import load_dotenv

load_dotenv()
from flask import Flask

from src.queuebert.api.slack_routes import slack_routes

app = Flask(__name__)
app.register_blueprint(slack_routes)

# Configure logging
if os.getenv("ENV") == "production":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == "__main__":
    app.run(port=8081)
