provider "google" {
  project     = var.project
  region      = "europe-west2"
  zone        = "europe-west2-c"
}

resource "google_storage_bucket" "bucket" {
  name     = "cloud-function-slackbot-publish"
  location = "EU"
}

resource "google_storage_bucket_object" "archive" {
  name   = "index.zip"
  bucket = google_storage_bucket.bucket.name
  source = "../../../../cloud_functions/slackbot_publish/index.zip"
}

resource "google_cloudfunctions_function" "function" {
  name        = "slackbot-publish"
  description = "Publish Events from Slack to Pub/Sub"
  runtime     = "python37"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  timeout               = 60
  entry_point           = "handle_event"
  labels = {
    my-label = "slackbot-dev"
  }

  environment_variables = {
    SLACK_SECRET       = var.SLACK_SECRET,
    SLACK_API_TOKEN    = var.SLACK_API_TOKEN,
  }
}

# IAM entry for a single user to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  ### - TO DO - improve authentication
  member = "allUsers"
}

# Create the Pub/Sub topic to publish to
resource "google_pubsub_topic" "slack-event-data" {
  name = "slack-event-data"
}