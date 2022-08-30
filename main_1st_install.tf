provider "google" {
  project = "gcp-ci-cd-drugs-data-pipeline"
}


resource "google_storage_bucket" "default" {
  name          = "gcp-ci-cd-drugs-data-pipeline-tfstate"
  force_destroy = false
  location      = "US"
  storage_class = "STANDARD"
  versioning {
    enabled = true
  }
}