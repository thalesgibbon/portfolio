# main.tf


module "apis" {
  source = "../modules/apis"
  project_id = var.project_id
}


module "pubsub" {
  source = "../modules/pubsub"
  project_id = var.project_id
}


module "storage" {
  source = "../modules/storage"
  bucket_name = var.bucket_name
  region = var.region
}

module "bigquery" {
  source = "../modules/bigquery"
  region = var.region
}
