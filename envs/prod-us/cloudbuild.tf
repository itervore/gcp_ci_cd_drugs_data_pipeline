
# /***********************************************
#  Cloud Build - Master branch triggers
#  ***********************************************/

# resource "google_cloudbuild_trigger" "master_trigger_deploy_composer" {
#   project     = var.project_id
#   description = "Composer deploy prod"

#   github {
#     owner = var.github_owner
#     name  = var.github_repo
#     push {
#       branch = "^main$"
#     }
#   }

#   substitutions = {
#     REPO_NAME                 = var.github_repo
#     _DATAFLOW_JAR_BUCKET_TEST = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-dataflow-source-test"].url, "gs://")
#     _DATAFLOW_JAR_FILE_LATEST = "latest.jar"
#     _DATAFLOW_JAR_BUCKET_PROD = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-dataflow-source-prod"].url, "gs://")
#     _COMPOSER_INPUT_BUCKET    = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-input-prod"].url, "gs://")
#     _COMPOSER_RESULT_BUCKET   = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-result-prod"].url, "gs://")
#     _COMPOSER_DAG_BUCKET      = google_composer_environment.composer-environment.config.0.dag_gcs_prefix
#     _COMPOSER_ENV_NAME        = google_composer_environment.composer-environment.name
#     _COMPOSER_REGION          = var.default_region
#     _COMPOSER_DAG_NAME_PROD   = "prod_python_data_pipeline"
#   }

#   filename = var.cloudbuild_deploy_prod_composer_filename
# }

# /***********************************************
#  Cloud Build - Non Master branch triggers
#  ***********************************************/


resource "google_cloudbuild_trigger" "non_master_trigger_build_deploy_flex_template" {
  for_each = fileset("../../source-code", "*.dockerfile")

  project     = var.project_id
  description = format("%s%s","Build Flex template : ", replace(trimsuffix(each.key, ".dockerfile"),"_","-"))

  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
        invert_regex = true
        branch = "^main$"
    }
  }

  substitutions = {
    REPO_NAME               = var.github_repo
    # _DATAFLOW_JAR_BUCKET    = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-dataflow-source-test"].url, "gs://") # Java

    _COMPOSER_INPUT_BUCKET  = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-input-test"].url, "gs://")
    _COMPOSER_REF_BUCKET    = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-ref-test"].url, "gs://")
    _COMPOSER_RESULT_BUCKET = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-result-test"].url, "gs://")


    _COMPOSER_DAG_BUCKET    = google_composer_environment.composer-environment.config.0.dag_gcs_prefix
    _COMPOSER_ENV_NAME      = google_composer_environment.composer-environment.name
    _COMPOSER_REGION        = var.default_region
    _COMPOSER_DAG_NAME_TEST = "test_python_data_pipeline"

    _REGION                 = var.default_region #Python
    _IMAGE_NAME             = format("%s_%s",var.target_gcr_image,trimsuffix(each.key, ".dockerfile"))
    _IMAGE_TAG              = var.target_gcr_image_tag
    _TEMPLATE_GCS_LOCATION  = format("%s/%s%s%s",google_storage_bucket.composer-dataflow-source-test["composer-dataflow-source-test"].url, "template/",trimsuffix(each.key, ".dockerfile"),"_spec.json") # Python
    _PIPELINE_NAME          = trimsuffix(each.key, ".dockerfile")
  }

  filename = var.cloudbuild_build_deploy_flex_template_filename

}

resource "google_cloudbuild_trigger" "non_master_trigger_deploy_composer" {
  project     = var.project_id
  description ="Deploy composer DAG"

  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
        invert_regex = true
        branch = "^main$"
    }
  }

  substitutions = {
    REPO_NAME               = var.github_repo
    # _DATAFLOW_JAR_BUCKET    = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-dataflow-source-test"].url, "gs://") # Java

    _COMPOSER_INPUT_BUCKET  = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-input-test"].url, "gs://")
    _COMPOSER_REF_BUCKET    = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-ref-test"].url, "gs://")
    _COMPOSER_RESULT_BUCKET = trimprefix(google_storage_bucket.composer-dataflow-source-test["composer-result-test"].url, "gs://")
    _COMPOSER_RESULTS_BQ     = format("%s:%s", 
                                    google_bigquery_dataset.bq_dataset_test.project,
                                    google_bigquery_dataset.bq_dataset_test.dataset_id)
    _COMPOSER_ERRORS_BQ     = format("%s:%s", 
                                    google_bigquery_dataset.bq_dataset_test.project,
                                    google_bigquery_dataset.bq_dataset_test.dataset_id)
    _COMPOSER_DAG_BUCKET    = google_composer_environment.composer-environment.config.0.dag_gcs_prefix
    _COMPOSER_ENV_NAME      = google_composer_environment.composer-environment.name
    _COMPOSER_REGION        = var.default_region
    _COMPOSER_DAG_NAME_TEST = "test_python_data_pipeline"

    _REGION                 = var.default_region #Python
    }

  filename = var.cloudbuild_deploy_test_composer_filename

}