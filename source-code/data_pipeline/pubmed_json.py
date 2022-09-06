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
import json
import re
from typing import NamedTuple
import apache_beam as beam
from google.cloud import storage, bigquery
from apache_beam.io.gcp import bigquery as beam_bigquery
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from pipeline.beam_classes.add_metadata import AddMetadataDoFn
from apache_beam import PCollection


import logging

def run():
  parser = argparse.ArgumentParser()
  parser.add_argument("--input-bucket", required=True, default="gs://gcp-ci-cd-drugs-data-pipeline-composer-input-test")
  parser.add_argument("--input-filename", required=True, default="pubmed.json")
  parser.add_argument("--results-bq-table", required=True, default="gcp-ci-cd-drugs-data-pipeline:gcp_ci_cd_drugs_data_pipeline.json_pubmed")
  parser.add_argument("--errors-bq-table", required=True, default="gcp-ci-cd-drugs-data-pipeline:gcp_ci_cd_drugs_data_pipeline.errors_json_pubmed")
  app_args, pipeline_args = parser.parse_known_args()

  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = True

  storage_client = storage.Client()
  bucket = storage_client.bucket( app_args.input_bucket.removeprefix("gs://")) 

  blob = bucket.blob(app_args.input_filename)
  contents = blob.download_as_string()
  RE_TRAILING_COMMA = re.compile(r',(?=\s*?[\}\]])')

  oneline_str = RE_TRAILING_COMMA.sub('', contents.decode())

  json_content = json.loads(oneline_str)

  print(json_content)

  # Construct a BigQuery client object.
  client = bigquery.Client()
  table = client.get_table(app_args.results_bq_table.split(':')[1])
  output_schema = table.schema
  print(output_schema)

  with beam.Pipeline(argv=pipeline_options) as p:

    json_content =  p | beam.Create(json_content)
    header_to_bq_header = {
      'id' : 'id',
      'title': 'article_title',
      'date' : 'date',
      'journal' : 'journal_title'
    }
    # def create_output_record(record , mapping):
    #   output_record = {}
    #   for key, value in record.items():
    #     if mapping.get(key):
    #       output_record[mapping[key]] = value
    #     else:
    #       output_record[key] = value
    #   return output_record

    output = json_content | beam.ParDo(AddMetadataDoFn(header_to_bq_header=header_to_bq_header, output_schema=output_schema)).with_outputs()

    cleaned_records: PCollection[NamedTuple] = output[AddMetadataDoFn.CORRECT_OUTPUT_TAG]
    cleaning_errors: PCollection[dict] = output[AddMetadataDoFn.WRONG_OUTPUT_TAG]


    (output |"output" >> beam.Map(print))

    cleaned_records | "Write results to BigQuery" >> beam.io.WriteToBigQuery(
      table=app_args.results_bq_table,
      create_disposition=beam_bigquery.BigQueryDisposition.CREATE_NEVER,
      write_disposition=beam_bigquery.BigQueryDisposition.WRITE_TRUNCATE)

    cleaning_errors | "Write errors to BigQuery" >> beam.io.WriteToBigQuery(
      table=app_args.errors_bq_table,
      create_disposition=beam_bigquery.BigQueryDisposition.CREATE_NEVER,
      write_disposition=beam_bigquery.BigQueryDisposition.WRITE_TRUNCATE)


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()