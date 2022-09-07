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

RUN_ID="$(date +%Y%m%d-%H%M%S)"

gcloud dataflow flex-template run "data-pipeline-${RUN_ID}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --template-file-gcs-location="${TEMPLATE_GCS_LOCATION}" \
  --parameters=input-bucket="${INPUT_BUCKET}/clinical_trials.csv",results-bq-table="${BQ_RESULTS}.clinical_trials",errors-bq-table="${BQ_ERRORS}.errors_clinical_trials",setup_file=${SETUP_FILE} \
  --temp-location="${TEMP_LOCATION}"