# Copyright 2019 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Data processing test workflow definition.
"""
import datetime
from airflow import models
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator

dataflow_staging_bucket = f"gs://{models.Variable.get('dataflow_staging_bucket_test')}/staging"

# dataflow_jar_location = 'gs://%s/%s' % (
#     models.Variable.get('dataflow_jar_location_test'),
#     models.Variable.get('dataflow_jar_file_test'))

project = "gcp-ci-cd-drugs-data-pipeline"
region = models.Variable.get('gcp_region')
zone = models.Variable.get('gcp_zone')
input_bucket = 'gs://' + models.Variable.get('gcs_input_bucket_test')
# output_bucket_name = models.Variable.get('gcs_output_bucket_test')
# output_bucket = 'gs://' + output_bucket_name
# ref_bucket = models.Variable.get('gcs_ref_bucket_test')
# output_prefix = 'output'
# download_task_prefix = 'download_result'

# QUOTA EXCEEDED
# output_bq_results = models.Variable.get('composer_results_bq')
# output_bq_errors = models.Variable.get('composer_errors_bq')
output_bq_results = "gcp-ci-cd-drugs-data-pipeline:gcp_ci_cd_drugs_data_pipeline"
output_bq_errors = "gcp-ci-cd-drugs-data-pipeline:gcp_ci_cd_drugs_data_pipeline"
template_gcs_location_drugs= "gs://gcp-ci-cd-drugs-data-pipeline-composer-dataflow-source-test/template/drugs_spec.json"
template_gcs_location_clinical_trials= "gs://gcp-ci-cd-drugs-data-pipeline-composer-dataflow-source-test/template/clinicals_trials_spec.json"

template_gcs_location_drugs_mention= "gs://gcp-ci-cd-drugs-data-pipeline-composer-dataflow-source-test/template/drugs_mention_spec.json"
template_gcs_location_pubmed= "gs://gcp-ci-cd-drugs-data-pipeline-composer-dataflow-source-test/template/pubmed_spec.json"

yesterday = datetime.datetime.combine(
    datetime.datetime.today() - datetime.timedelta(1),
    datetime.datetime.min.time())

default_args = {
    'dataflow_default_options': {
        'project': project,
        'zone': zone,
        'region': region,
        'stagingLocation': dataflow_staging_bucket
    }
}

def get_flex_template_operator(gcs_template_path, task_name, parameters ):
    flex_template_operator = DataflowStartFlexTemplateOperator(
        task_id=task_name,
        body={
            "launchParameter": {
                "containerSpecGcsPath": gcs_template_path,
                "jobName": "dataflow-flex-template-"+task_name,
                "parameters": parameters,
            }
        },
        do_xcom_push=True,
        location=region,
        start_date=yesterday
    )
    return flex_template_operator

with models.DAG(
    'test_python_data_pipeline',
    schedule_interval=None,
    default_args=default_args) as dag:

  load_drugs_parameters = {
    "input_bucket":f"{input_bucket}/drugs.csv",
    "results_bq_table":f"${output_bq_results}.drugs",
    "errors_bq_table": f"${output_bq_errors}.errors_drugs",
    "setup_file": "/dataflow/template/data_pipeline/setup.py"
  }

  dataflow_load_drugs = get_flex_template_operator(template_gcs_location_drugs,'drugs', load_drugs_parameters)

  load_clinical_trials_parameters = {
    "input_bucket":f"{input_bucket}/clinical_trials.csv",
    "results_bq_table":f"${output_bq_results}.clinical_trials",
    "errors_bq_table": f"${output_bq_errors}.errors_clinical_trials",
    "setup_file": "/dataflow/template/data_pipeline/setup.py"
  }

  dataflow_load_clinical_trials = get_flex_template_operator(template_gcs_location_clinical_trials,'clinicals-trials', load_clinical_trials_parameters)


  dataflow_load_drugs

  dataflow_load_clinical_trials

#   download_expected = GoogleCloudStorageDownloadOperator(
#       task_id='download_ref_string',
#       bucket=ref_bucket,
#       object='ref.txt',
#       store_to_xcom_key='ref_str',
#       start_date=yesterday
#   )
#   download_result_one = GoogleCloudStorageDownloadOperator(
#       task_id=download_task_prefix+'_1',
#       bucket=output_bucket_name,
#       object=output_prefix+'-00000-of-00003',
#       store_to_xcom_key='res_str_1',
#       start_date=yesterday
#   )
#   download_result_two = GoogleCloudStorageDownloadOperator(
#       task_id=download_task_prefix+'_2',
#       bucket=output_bucket_name,
#       object=output_prefix+'-00001-of-00003',
#       store_to_xcom_key='res_str_2',
#       start_date=yesterday
#   )
#   download_result_three = GoogleCloudStorageDownloadOperator(
#       task_id=download_task_prefix+'_3',
#       bucket=output_bucket_name,
#       object=output_prefix+'-00002-of-00003',
#       store_to_xcom_key='res_str_3',
#       start_date=yesterday
#   )
#   compare_result = CompareXComMapsOperator(
#       task_id='do_comparison',
#       ref_task_ids=['download_ref_string'],
#       res_task_ids=[download_task_prefix+'_1',
#                     download_task_prefix+'_2',
#                     download_task_prefix+'_3'],
#       start_date=yesterday
#   )

#   dataflow_execution >> download_result_one
#   dataflow_execution >> download_result_two
#   dataflow_execution >> download_result_three

#   download_expected >> compare_result
#   download_result_one >> compare_result
#   download_result_two >> compare_result
#   download_result_three >> compare_result