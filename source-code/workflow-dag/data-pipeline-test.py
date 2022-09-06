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

# QUOTA EXCEEDED, can't update composer anymore
# output_bq_results = models.Variable.get('composer_results_bq')
# output_bq_errors = models.Variable.get('composer_errors_bq')
output_bq_results = "gcp-ci-cd-drugs-data-pipeline:gcp_ci_cd_drugs_data_pipeline"
output_bq_errors = "gcp-ci-cd-drugs-data-pipeline:gcp_ci_cd_drugs_data_pipeline"
template_gcs_location_drugs= "gs://gcp-ci-cd-drugs-data-pipeline-composer-dataflow-source-test/template/drugs_spec.json"
template_gcs_location_clinical_trials= "gs://gcp-ci-cd-drugs-data-pipeline-composer-dataflow-source-test/template/clinical_trials_spec.json"

template_gcs_location_drugs_mention= "gs://gcp-ci-cd-drugs-data-pipeline-composer-dataflow-source-test/template/drugs_mention_spec.json"
template_gcs_location_pubmed= "gs://gcp-ci-cd-drugs-data-pipeline-composer-dataflow-source-test/template/pubmed_spec.json"
template_gcs_location_pubmed_json= "gs://gcp-ci-cd-drugs-data-pipeline-composer-dataflow-source-test/template/pubmed_json_spec.json"
template_gcs_location_pubmed_csv= "gs://gcp-ci-cd-drugs-data-pipeline-composer-dataflow-source-test/template/pubmed_csv_spec.json"


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
                "jobName": task_name.replace("_","-"),
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
    "input-bucket":f"{input_bucket}/drugs.csv",
    "results-bq-table":f"${output_bq_results}.drugs",
    "errors-bq-table": f"${output_bq_errors}.errors_drugs",
    "setup_file": "/dataflow/template/data_pipeline/setup.py"
  }

  dataflow_load_drugs = get_flex_template_operator(template_gcs_location_drugs,'drugs_data_pipeline', load_drugs_parameters)

  load_clinical_trials_parameters = {
    "input-bucket":f"{input_bucket}/clinical_trials.csv",
    "results-bq-table":f"${output_bq_results}.clinical_trials",
    "errors-bq-table": f"${output_bq_errors}.errors_clinical_trials",
    "setup_file": "/dataflow/template/data_pipeline/setup.py"
  }

  dataflow_load_clinical_trials = get_flex_template_operator(template_gcs_location_clinical_trials,'clinicals_trials_data_pipeline', load_clinical_trials_parameters)

  load_pubmed_csv_parameters = {
    "input-bucket":f"{input_bucket}/pubmed.csv",
    "results-bq-table":f"${output_bq_results}.csv_pubmed",
    "errors-bq-table": f"${output_bq_errors}.errors_csv_pubmed",
    "setup_file": "/dataflow/template/data_pipeline/setup.py"
  }

  dataflow_load_pubmed_csv = get_flex_template_operator(template_gcs_location_pubmed_csv,'pubmed_csv_data_pipeline', load_pubmed_csv_parameters)

  load_pubmed_json_parameters = {
    "input-bucket":f"{input_bucket}",
    "input-filename":"pubmed.json",
    "results-bq-table":f"${output_bq_results}.json_pubmed",
    "errors-bq-table": f"${output_bq_errors}.errors_json_pubmed",
    "setup_file": "/dataflow/template/data_pipeline/setup.py"
  }

  dataflow_load_pubmed_json = get_flex_template_operator(template_gcs_location_pubmed_json,'pubmed_json_data_pipeline', load_pubmed_json_parameters)

  load_pubmed_parameters = {
    "input-csv-bq-table":f"{output_bq_results}.csv_pubmed",
    "input-json-bq-table":f"{output_bq_results}.json_pubmed",
    "results-bq-table":f"${output_bq_results}.pubmed",
    "setup_file": "/dataflow/template/data_pipeline/setup.py"
  }

  dataflow_load_pubmed = get_flex_template_operator(template_gcs_location_pubmed,'pubmed_data_pipeline', load_pubmed_parameters)

  load_drugs_mention_parameters = {
    "bq-drug-table":f"{output_bq_results}.drugs",
    "bq-clinicals-trials-table":f"{output_bq_results}.clinical_trials",
    "bq-pubmed-table":f"{output_bq_results}.pubmed",
    "results-bucket":f"gs://gcp-ci-cd-drugs-data-pipeline-composer-result-test",
    "results-bq-table":f"${output_bq_results}.drug_mention",
    "errors-bq-table":f"${output_bq_results}.errors_drug_mention",
    "setup_file": "/dataflow/template/data_pipeline/setup.py"
  }

  dataflow_load_drugs_mention = get_flex_template_operator(template_gcs_location_drugs_mention,'drug_mention_data_pipeline', load_drugs_mention_parameters)


  dataflow_load_drugs
  dataflow_load_clinical_trials
  dataflow_load_pubmed_json >>  dataflow_load_pubmed
  dataflow_load_pubmed_csv  >>  dataflow_load_pubmed

  dataflow_load_pubmed            >>  dataflow_load_drugs_mention
  dataflow_load_clinical_trials   >>  dataflow_load_drugs_mention
  dataflow_load_drugs             >>  dataflow_load_drugs_mention