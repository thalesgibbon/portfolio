# modules/apis/main.tf

resource "google_project_service" "required_apis" {
  for_each = toset([
    "iam.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "pubsub.googleapis.com",
    "dataflow.googleapis.com",
  ])

  project = var.project_id
  service = each.key
}
