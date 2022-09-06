resource "random_id" "composer_random" {
  byte_length = 8
}

resource "google_composer_environment" "composer-environment" {
  name    = "composer-${random_id.composer_random.hex}"
  region  = var.default_region
  project = var.project_id

  config {
    node_config {
      network         = "default"
      subnetwork      = "default"
      service_account = "${data.google_project.my_project.number}-compute@developer.gserviceaccount.com"
    }
    software_config {
      image_version = "composer-2-airflow-2"
      env_variables = {
        AIRFLOW_VAR_GCP_PROJECT                  = var.project_id
        AIRFLOW_VAR_GCP_REGION                   = var.default_region
        AIRFLOW_VAR_GCP_ZONE                     = var.default_zone
        AIRFLOW_VAR_DATAFLOW_JAR_LOCATION_TEST   = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-dataflow-source-test"].url, "gs://")
        # airflow_var_dataflow_jar_file_test       = "to_be_overriden"
        # var_dataflow_jar_file_test               = "to_be_overriden"
        AIRFLOW_VAR_GCS_INPUT_BUCKET_TEST        = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-input-test"].url, "gs://")
        AIRFLOW_VAR_GCS_REF_BUCKET_TEST          = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-ref-test"].url, "gs://")
        AIRFLOW_VAR_GCS_OUTPUT_BUCKET_TEST       = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-result-test"].url, "gs://")
        AIRFLOW_VAR_DATAFLOW_STAGING_BUCKET_TEST = trimprefix(google_storage_bucket.composer-dataflow-source-test["dataflow-staging-test"].url, "gs://")
        AIRFLOW_VAR_DATAFLOW_JAR_LOCATION_PROD   = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-dataflow-source-prod"].url, "gs://")
        # airflow_var_dataflow_jar_file_prod       = "to_be_overriden"
        # var_dataflow_jar_file_prod               = "to_be_overriden"
        AIRFLOW_VAR_GCS_INPUT_BUCKET_PROD        = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-input-prod"].url, "gs://")
        AIRFLOW_VAR_GCS_OUTPUT_BUCKET_PROD       = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-result-prod"].url, "gs://")
        AIRFLOW_VAR_DATAFLOW_STAGING_BUCKET_PROD = trimprefix(google_storage_bucket.composer-dataflow-source-test["dataflow-staging-prod"].url, "gs://")
      }    
    }
    environment_size = "ENVIRONMENT_SIZE_SMALL"

  }
  depends_on = [
    google_project_iam_member.composer_admin_V2,
    google_project_iam_member.composer_admin
  ]
}

resource "google_project_iam_member" "composer_admin_V2" {
  project = var.project_id
  role    = "roles/composer.ServiceAgentV2Ext"
  member  = "serviceAccount:service-${data.google_project.my_project.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "composer_admin" {
  project = var.project_id
  role    = "roles/composer.admin"
  member  = "serviceAccount:service-${data.google_project.my_project.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}


resource "google_project_iam_member" "composer_worker" {
  project = var.project_id
  role    = "roles/composer.worker"
  member  = "serviceAccount:service-${data.google_project.my_project.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}