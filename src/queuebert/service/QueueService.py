import json

import jinja2

from src.queuebert.service.client.SlackClient import SlackClient


def find_user_position_in_queue(user_id, blocks):
    for i, block in enumerate(blocks):
        if block["type"] == "section":
            if user_id in block["text"]["text"]:
                return i
    return None


class QueueService:
    def __init__(self, slack_client: SlackClient = SlackClient()):
        self.slack_client = slack_client
        self.environment = jinja2.Environment()
        self.position_template = self.fetch_position_template()

    def join(self, body):
        if find_user_position_in_queue(body["user"]["id"], body["message"]["blocks"]) is not None:
            # Todo: Add message that you can't join multiple times
            return

        old_message = body["message"]
        position = len(old_message["blocks"]) - 1
        person = f"<@{body["user"]["id"]}>"
        rendered_template = self.position_template.render(position=position, person=person)
        old_message["blocks"].insert(-1, json.loads(rendered_template))
        self.slack_client.update(body["container"]["channel_id"], body["container"]["message_ts"],
                                 old_message["blocks"])

    def fetch_position_template(self):
        with open("src/queuebert/templates/position_template.json", "r") as position_template:
            template_string = position_template.read()
            return self.environment.from_string(template_string)

    def leave(self, body):
        position = find_user_position_in_queue(body["user"]["id"], body["message"]["blocks"])
        if position is not None:
            body["message"]["blocks"].pop(position)
            for p in range(len(body["message"]["blocks"]) - 1):
                parts = body["message"]["blocks"][p]["text"]["text"].split(" ")
                if parts[0].isdigit():
                    new_number = int(parts[0]) - 1
                    body["message"]["blocks"][p]["text"]["text"] = f"{new_number} {parts[1]}"
            self.slack_client.update(body["container"]["channel_id"], body["container"]["message_ts"],
                                     body["message"]["blocks"])

    def queue_action(self, body):
        match body["actions"][0]["action_id"]:
            case "join":
                return self.join(body)
            case "leave":
                return self.leave(body)

    def start_new_queue(self, body):
        with open("src/queuebert/templates/queue_template.json", "r") as queue_template:
            queue_blocks = json.load(queue_template)
            self.slack_client.send_message_with_blocks(body["channel_id"], "", queue_blocks)
