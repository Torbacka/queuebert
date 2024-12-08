import json

from flask import request, Blueprint, Response, current_app

from src.queuebert.security.verify_signature import verify_slack_signature
from src.queuebert.service.OauthService import OauthService
from src.queuebert.service.QueueService import QueueService

slack_routes = Blueprint("slack_routes", __name__)
queue_service = QueueService()
oauth_service = OauthService()

@slack_routes.route("/interactivity", methods=["POST"])
@verify_slack_signature()
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

@slack_routes.route("/create", methods=["POST"])
@verify_slack_signature()
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
    return Response(status=200)


@slack_routes.route("/oauth/callback", methods=["GET"])
def oauth_callback():
    current_app.logger.info(f"Start processing oauth callback")
    # Get the authorization code from the query parameters
    auth_code = request.args.get('code')
    if not auth_code:
        return Response("Missing authorization code", 400)
    response, code = oauth_service.getAccessToken(auth_code)

    return Response(response=response, status=200)