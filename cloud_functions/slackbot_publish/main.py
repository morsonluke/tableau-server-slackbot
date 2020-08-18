import os
import json
from flask import make_response, request
from time import time
import hmac
import hashlib
from slack import WebClient
from publish import publish_event_data

client = WebClient(token=os.environ['SLACK_API_TOKEN'])


def verify_signature(timestamp, signature):

    signing_secret = os.environ['SLACK_SECRET']

    # Compare the generated hash and incoming request signature
    if hasattr(hmac, "compare_digest"):
        req = str.encode('v0:' + str(timestamp) + ':') + request.get_data()
        request_hash = 'v0=' + hmac.new(
            str.encode(signing_secret),
            req, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(request_hash, signature)


def handle_event(request):

    if request.method != 'POST':
        return 'Only POST requests are accepted', 405

    # Parse the request payload into JSON
    event_data = json.loads(request.data.decode('utf-8'))

    # Echo the URL verification challenge code back to Slack
    if "challenge" in event_data:
        return make_response(
            event_data.get("challenge"), 200, {"content_type": "application/json"}
        )

    # Each request comes with request timestamp and request signature
    req_timestamp = request.headers.get('X-Slack-Request-Timestamp')
    if abs(time() - int(req_timestamp)) > 60 * 5:
        return make_response("", 403)

    # Verify the request signature using the signing secret
    req_signature = request.headers.get('X-Slack-Signature')
    if not verify_signature(req_timestamp, req_signature):
        return make_response("", 403)

    # Emit the event
    if "event" in event_data:

        # Publish data to Pub/Sub Topic on "app_mention"
        if event_data['event']['type'] == 'app_mention':
            publish_event_data(request.get_data())

        # Slack API expects a response in 3 seconds
        response = make_response("", 200)
        return response
