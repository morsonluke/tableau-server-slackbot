"""Publishes multiple messages to a Pub/Sub topic with an error handler."""
import os
from google.cloud import pubsub_v1

# Env variable is set automatically
gcp_project = os.environ.get('GCP_PROJECT')

project_id = gcp_project
topic_id = "slack-event-data"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

futures = dict()


def get_callback(f, data):
    def callback(f):
        try:
            print(f.result())
            futures.pop(data)
        except:  # noqa
            print("Please handle {} for {}.".format(f.exception(), data))

    return callback


def publish_event_data(event_data):
    data = event_data
    futures.update({data: None})
    # When you publish a message, the client returns a future.
    future = publisher.publish(
        topic_path, data=data  # data must be a bytestring
    )
    futures[data] = future
    # Publish failures shall be handled in the callback function.
    future.add_done_callback(get_callback(future, data))
