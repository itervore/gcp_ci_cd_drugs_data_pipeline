variable "org_id" {
  description = "GCP Organization ID"
  type        = string
}

variable "billing_account" {
  description = "The ID of the billing account to associate projects with."
  type        = string
}

variable "project_id" {
    description = "This is the project id from GCP"
}

variable "project_name" {
    description = "This is the project id from GCP"
}

variable "location" {
    description = "GCP Location"
}

variable "default_region" {
  description = "Default region to create resources where applicable."
  type        = string
  default     = "us-west1"
}

variable "default_zone" {
  description = "Default zone to create resources where applicable."
  type        = string
  default     = "us-west1-a"
}

variable "github_owner" {
  description = "Owner of the github repository"
}

variable "github_repo" {
  description = "Name of the github repository"
}

variable "cloudbuild_deploy_prod_composer_filename" {
  description = "Path and name of Cloud Build YAML definition used to deploy prod composer."
  type        = string
  default     = "source-code/deploy_prod.yaml"
}

variable "cloudbuild_deploy_test_composer_filename" {
  description = "Path and name of Cloud Build YAML definition used to deploy test composer."
  type        = string
  default     = "source-code/build_deploy_test.yaml"
}

variable "target_gcr_image" {
  description = "name of image for dataflow pipeline."
  type        = string
  default     = "dataflow_flex_data_pipeline"
}

variable "target_gcr_image_tag" {
  description = "tag of image for dataflow pipeline"
  type        = string
  default     = "python"
}


variable "bq_path_to_schemas" {
  description = "Local path to bq schemas"
  default     = "bigquery_schema"
}