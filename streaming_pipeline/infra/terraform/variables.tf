variable "project_id" {
  description = "Google Cloud project id"
  type        = string
}

variable "region" {
  description = "Region para implantar o serviço Cloud Run"
  type        = string
  default     = "us-central1"
}