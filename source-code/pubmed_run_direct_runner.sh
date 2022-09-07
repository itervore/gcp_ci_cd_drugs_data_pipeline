#!/bin/sh

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

python source-code/data_pipeline/pubmed.py --runner=DirectRunner \
  --project-id="${PROJECT_ID}" \
  --input-csv-bq-table="${BQ_RESULTS}.csv_pubmed" \
  --input-json-bq-table="${BQ_RESULTS}.json_pubmed" \
  --results-bq-table="${BQ_RESULTS}.pubmed" \
  --temp_location="${TEMP_LOCATION}"