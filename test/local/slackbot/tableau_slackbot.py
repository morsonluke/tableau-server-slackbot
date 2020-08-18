from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import os
from tableau_api import generate_report, list
from flask import Flask
import threading, queue
import time

app = Flask(__name__)

lock = threading.Lock()
queue = queue.Queue()

# Location to generate image
view_location = os.environ["VIEW_FILE_LOCATION"]

# Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)

# Create a SlackClient for the bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = SlackClient(slack_bot_token)


@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    channel = message["channel"]

    if message.get("bot_id") is None:
        text = message.get('text')

        if "help" in text:
            message = "\n\n  *How to use the Tableau Slackbot* :robot_face: : \n" \
                      "\n 1. `list @tableau_server_app`: list views available to output to Slack" \
                      "\n\n 2. `gimmie @tableau_server_app What If Forecast`: generate the report"
            slack_client.api_call("chat.postMessage", channel=channel, text=message)

        if "list" in text:
            message = list('view')
            slack_client.api_call("chat.postMessage", channel=channel, text=message)

        if "gimmie" in text:
            queue.put(event_data)


def worker():
    while True:
        event_data = queue.get()
        message = event_data["event"]
        channel = message["channel"]

        view = event_data["event"]["blocks"][0]["elements"][0]["elements"][2]["text"]
        view_list = list('view')
        if view.strip() in view_list:
            generate_report(view)
            slack_client.api_call('files.upload',
                                  channels="{0}".format(channel),
                                  user = 'tableau_bot',
                                  filename="{0}.png".format(view),
                                  file=open("{0}/view.png".format(view_location), 'rb'))

            # Delete the view generated locally
            if os.path.exists("{0}/view.png".format(view_location)):
                os.remove("{0}/view.png".format(view_location))
            else:
                print("The file does not exist")
        else:
            message = ":smirk: That view does not exist. Try again." \
                      "See the available views with: `list @tableau_server_app Global Temperatures`"
            slack_client.api_call("chat.postMessage", channel=channel, text=message)

        time.sleep(0.5)


# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))


report_thread = threading.Thread(
    target=worker
).start()

app.run(port=3000)

queue.join()
