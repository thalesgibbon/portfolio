# modules/apis/main.tf

resource "google_storage_bucket" "datalake_bucket" {
  name     = var.bucket_name
  location = var.region
}
