import os
import base64
import time
from slack import WebClient
import json
from tableau_api import generate_report, list

client = WebClient(token=os.environ['SLACK_API_TOKEN'])


def pubsub_consume(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    event_data = json.loads(pubsub_message)

    message = event_data['event']
    channel = message['channel']

    if message.get('bot_id') is None:
        text = message.get('text')

        if "help" in text:
            slack_text = "\n\n  *How to use the Tableau Slackbot* :robot_face: : \n" \
                         "\n 1. `list @tableau_server_app`: list views available to output to Slack" \
                         "\n\n 2. `gimmie @tableau_server_app What If Forecast`: generate the report"
            response = client.chat_postMessage(
                        channel=channel,
                        text=slack_text)
            return response

        if "list" in text:
            slack_text = list('view')
            response = client.chat_postMessage(
                        channel=channel,
                        text=slack_text)
            return response

        if "gimmie" in text:

            filepath = time.strftime("%Y%m%d-%H%M%S")
            view = event_data['event']['blocks'][0]['elements'][0]['elements'][2]['text']
            view_list = list('view')
            if view.strip() in view_list:
                generate_report(view, filepath)

                # Upload view from /tmp to Slack
                response = client.files_upload(
                    channels=channel,
                    file="/tmp/view_{0}.png".format(filepath),
                    title="View"
                )

                # Delete the view generated locally
                if os.path.exists("/tmp/view_{0}.png".format(filepath)):
                    os.remove("/tmp/view_{0}.png".format(filepath))

            else:
                slack_text = ":shrug: See the available views with: `list @tableau_server_app`"
                response = client.chat_postMessage(
                        channel=channel,
                        text=slack_text)

            return response
