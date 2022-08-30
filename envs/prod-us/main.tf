locals {
  env = "prod-us"
}

terraform {
  backend "gcs" {
      bucket = "gcp-ci-cd-drugs-data-pipeline-tfstate"
      prefix = "env/prod-us"
    }
}

provider "google" {
  project = "${var.project}"
}


resource "google_storage_bucket" "ingress_bucket" {
  name          = "gcp-ci-cd-drugs-data-pipeline-ingress-bucket"
  force_destroy = false
  location      = "US"
  storage_class = "STANDARD"
}
