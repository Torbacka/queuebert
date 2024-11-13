import json

from flask import request, Blueprint, Response

from security.verify_signature import verify_slack_signature
from service.QueueService import QueueService

slack_routes = Blueprint("slack_routes", __name__)
queue_service = QueueService()

@slack_routes.route("/interactivity", methods=["POST"])
@verify_slack_signature
def slack_interactivity():
    """
    All incoming interactive messages are sent to this endpoint
    :return: Response with 200 status code
    """
    body = json.loads(request.form['payload'])
    match body["type"]:
        case "block_actions":
            queue_service.queue_action(body)
        case _:
            print(f"Unhandled action: {body["type"]}")

    return Response(status=200)

@slack_routes.route("/create", methods=["POST", "GET"])
@verify_slack_signature
def create_queue():
    """
    Slash command to create a new queue

    token
    team_id
    team_domain
    channel_id
    channel_name
    user_id
    user_name
    command
    text
    api_app_id
    is_enterprise_install
    response_url
    trigger_id
    :return:
    """
    body = request.form
    queue_service.start_new_queue(body)
    return Response(body["challenge"], status=200, content_type="text/plain")