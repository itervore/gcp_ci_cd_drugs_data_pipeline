#   Copyright 2021 Google LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import argparse
import apache_beam as beam
from apache_beam.io.gcp import bigquery
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
import logging

def run():
  parser = argparse.ArgumentParser()
  parser.add_argument("--input-csv-bq-table", required=True, default="gcp-ci-cd-drugs-data-pipeline:gcp_ci_cd_drugs_data_pipeline.csv_pubmed")
  parser.add_argument("--input-json-bq-table", required=True, default="gcp-ci-cd-drugs-data-pipeline:gcp_ci_cd_drugs_data_pipeline.json_pubmed")

  parser.add_argument("--results-bq-table", required=True, default="gcp-ci-cd-drugs-data-pipeline:gcp_ci_cd_drugs_data_pipeline.pubmed")
  app_args, pipeline_args = parser.parse_known_args()

  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = True

  with beam.Pipeline(argv=pipeline_options) as p:

    csv_input =  p | 'Reading  table : csv_input' >> bigquery.ReadFromBigQuery(
      table=app_args.input_csv_bq_table)

    json_input =  p | 'Reading  table : json_input' >> bigquery.ReadFromBigQuery(
      table=app_args.input_json_bq_table)

    merged = ((csv_input, json_input) | 'Merge PCollections' >> beam.Flatten())
    # ELT: Load.
    merged | "Write results to BigQuery" >> beam.io.WriteToBigQuery(
      table=app_args.results_bq_table,
      create_disposition=bigquery.BigQueryDisposition.CREATE_NEVER,
      write_disposition=bigquery.BigQueryDisposition.WRITE_TRUNCATE)

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()