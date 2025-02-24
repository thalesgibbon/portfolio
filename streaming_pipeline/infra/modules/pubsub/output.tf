# modules/datalake/output.tf

output "subscription_name" {
  value = google_pubsub_subscription.general_subscription.name
}
