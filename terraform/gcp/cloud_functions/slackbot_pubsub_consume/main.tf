provider "google" {
  project     = var.project
  region      = "europe-west2"
  zone        = "europe-west2-c"
}

resource "google_storage_bucket" "bucket" {
  name     = "cloud-function-slackbot-pubsub-consume"
  location = "EU"
}

resource "google_storage_bucket_object" "archive" {
  name   = "index.zip"
  bucket = google_storage_bucket.bucket.name
  source = "../../../../cloud_functions/slackbot_consume/index.zip"
}

resource "google_cloudfunctions_function" "function" {
  name        = "slackbot-pubsub-consume"
  description = "Consume Events from Pub/Sub and call the Tableau API"
  runtime     = "python37"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = "projects/${var.project}/topics/slack-event-data"
  }

  timeout     = 60
  entry_point = "pubsub_consume"
  labels = {
    my-label = "slackbot-dev"
  }

  environment_variables = {
    SLACK_SECRET       = var.SLACK_SECRET,
    SLACK_API_TOKEN    = var.SLACK_API_TOKEN,
    TABLEAU_TOKEN      = var.TABLEAU_TOKEN,
    TABLEAU_SERVER_URL = var.TABLEAU_SERVER_URL,
  }
}

# IAM entry for a single user to invoke the function
#resource "google_cloudfunctions_function_iam_member" "invoker" {
#  project        = google_cloudfunctions_function.function.project
#  region         = google_cloudfunctions_function.function.region
#  cloud_function = google_cloudfunctions_function.function.name

#  role = "roles/cloudfunctions.invoker"
#  member = "user:"
#}