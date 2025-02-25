# modules/apis/main.tf

resource "google_pubsub_topic" "backend_events_topic" {
  name = "backend-events-topic"
}

resource "google_pubsub_subscription" "general_subscription" {
  name  = "backend-events-topic-sub"
  topic = google_pubsub_topic.backend_events_topic.name
}
