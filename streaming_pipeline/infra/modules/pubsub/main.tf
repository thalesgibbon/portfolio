# modules/apis/main.tf

resource "google_pubsub_topic" "backend_events_topic" {
  name = "backend-events-topic"
}

resource "google_pubsub_subscription" "order_subscription" {
  name  = "order-subscription"
  topic = google_pubsub_topic.backend_events_topic.name
  filter = "attributes.type=\"order\""
}

resource "google_pubsub_subscription" "inventory_subscription" {
  name  = "inventory-subscription"
  topic = google_pubsub_topic.backend_events_topic.name
  filter = "attributes.type=\"inventory\""
}

resource "google_pubsub_subscription" "user_activity_subscription" {
  name  = "user_activity-subscription"
  topic = google_pubsub_topic.backend_events_topic.name
  filter = "attributes.type=\"user_activity\""
}
