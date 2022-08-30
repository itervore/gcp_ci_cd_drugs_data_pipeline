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
