# main.tf


module "apis" {
  source = "../modules/apis"
  project_id = var.project_id
}


module "pubsub" {
  source = "../modules/pubsub"
  project_id = var.project_id
}
