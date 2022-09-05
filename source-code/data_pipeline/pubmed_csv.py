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
from apache_beam.io.gcp import bigquery as beam_bigquery
from google.cloud import bigquery
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from pipeline.beam_classes.extract import ExtractDataTransform
import logging


def run():
  parser = argparse.ArgumentParser()
  parser.add_argument("--input-bucket", required=True)
  parser.add_argument("--results-bq-table", required=True)
  parser.add_argument("--errors-bq-table", required=True)
  app_args, pipeline_args = parser.parse_known_args()

  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = True

  # Construct a BigQuery client object.
  client = bigquery.Client()
  table = client.get_table(app_args.results_bq_table.split(':')[1])
  output_schema = table.schema

  with beam.Pipeline(options=pipeline_options) as p:
    # ELT: Extract.
    header = 'id,title,date,journal'
    header_to_bq_header = {
        'id' : 'id',
        'title': 'article_title',
        'date' : 'date',
        'journal' : 'journal_title'
      }
    
    sep = ','

    results, parsing_errors = p | "Extract and Parse" >> ExtractDataTransform(app_args.input_bucket, header , sep, header_to_bq_header, output_schema )

    results | "Write results to BigQuery" >> beam.io.WriteToBigQuery(
      table=app_args.results_bq_table,
      create_disposition=beam_bigquery.BigQueryDisposition.CREATE_NEVER,
      write_disposition=beam_bigquery.BigQueryDisposition.WRITE_TRUNCATE)

    parsing_errors | "Write errors to BigQuery" >> beam.io.WriteToBigQuery(
      table=app_args.errors_bq_table,
      create_disposition=beam_bigquery.BigQueryDisposition.CREATE_NEVER,
      write_disposition=beam_bigquery.BigQueryDisposition.WRITE_TRUNCATE)

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()