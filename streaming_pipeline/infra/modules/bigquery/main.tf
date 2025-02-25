resource "google_bigquery_dataset" "raw_events" {
  dataset_id = "raw_events"
  location   = var.region
}

resource "google_bigquery_table" "order" {
  dataset_id = google_bigquery_dataset.raw_events.dataset_id
  table_id   = "order"
  schema = jsonencode([
    {"name": "event_type", "type": "STRING", "mode": "REQUIRED"},
    {"name": "order_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "customer_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "order_date", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {"name": "status", "type": "STRING", "mode": "REQUIRED"},
    {"name": "items", "type": "RECORD", "mode": "REPEATED", "fields": [
      {"name": "product_id", "type": "STRING", "mode": "REQUIRED"},
      {"name": "product_name", "type": "STRING", "mode": "REQUIRED"},
      {"name": "quantity", "type": "INTEGER", "mode": "REQUIRED"},
      {"name": "price", "type": "FLOAT", "mode": "REQUIRED"}
    ]},
    {"name": "shipping_address", "type": "RECORD", "mode": "REQUIRED", "fields": [
      {"name": "street", "type": "STRING", "mode": "REQUIRED"},
      {"name": "city", "type": "STRING", "mode": "REQUIRED"},
      {"name": "country", "type": "STRING", "mode": "REQUIRED"}
    ]},
    {"name": "total_amount", "type": "FLOAT", "mode": "REQUIRED"}
  ])

  time_partitioning {
    type = "DAY"
    field = "order_date"
  }

  clustering = ["status", "customer_id", "order_id"]

  deletion_protection = false
}

resource "google_bigquery_table" "inventory" {
  dataset_id = google_bigquery_dataset.raw_events.dataset_id
  table_id   = "inventory"
  schema = jsonencode([
    {"name": "event_type", "type": "STRING", "mode": "REQUIRED"},
    {"name": "inventory_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "product_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "warehouse_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "quantity_change", "type": "INTEGER", "mode": "REQUIRED"},
    {"name": "reason", "type": "STRING", "mode": "REQUIRED"},
    {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"}
  ])

  time_partitioning {
    type = "DAY"
    field = "timestamp"
  }

  clustering = ["product_id", "warehouse_id", "event_type"]

  deletion_protection = false
}

resource "google_bigquery_table" "user_activity" {
  dataset_id = google_bigquery_dataset.raw_events.dataset_id
  table_id   = "user_activity"
  schema = jsonencode([
    {"name": "event_type", "type": "STRING", "mode": "REQUIRED"},
    {"name": "user_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "activity_type", "type": "STRING", "mode": "REQUIRED"},
    {"name": "ip_address", "type": "STRING", "mode": "REQUIRED"},
    {"name": "user_agent", "type": "STRING", "mode": "REQUIRED"},
    {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {"name": "metadata", "type": "RECORD", "mode": "REQUIRED", "fields": [
      {"name": "session_id", "type": "STRING", "mode": "REQUIRED"},
      {"name": "platform", "type": "STRING", "mode": "REQUIRED"}
    ]}
  ])

  time_partitioning {
    type = "DAY"
    field = "timestamp"
  }

  clustering = ["activity_type", "user_id", "event_type"]

  deletion_protection = false
}
