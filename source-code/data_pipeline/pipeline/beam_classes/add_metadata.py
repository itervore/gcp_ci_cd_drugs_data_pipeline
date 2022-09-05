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

from typing import Iterable, Dict

from apache_beam import DoFn
import datetime as dt
from apache_beam.metrics import Metrics
from apache_beam import DoFn, pvalue
import dateutil.parser



class AddMetadataDoFn(DoFn):
  CORRECT_OUTPUT_TAG = 'accommodations'
  WRONG_OUTPUT_TAG = 'parse_errors'
  
  def __init__(self, header_to_bq_header=None, output_schema=None, *unused_args, **unused_kwargs):
        self.header_to_bq_header = header_to_bq_header
        self.output_schema = output_schema
            # Metrics to report the number of records
        self.input_records_counter = Metrics.counter("ParseCSVDoFn", 'input_records')
        self.correct_records_counter = Metrics.counter("ParseCSVDoFn", 'correct_records')
        self.wrong_records_counter = Metrics.counter("ParseCSVDoFn", 'wrong_records')
        super()

  def get_output_key(self, key):
    output_key = key
    if self.header_to_bq_header:
        output_key = self.header_to_bq_header.get(key, key)
    return output_key


  def apply_output_type(self, output_key, value):
    output_value = value
    if self.output_schema:
        output_type = next(iter([ field.field_type for field in self.output_schema if field.name == output_key]), None)
        if output_type in ['DATE', 'DATETIME']:
            output_value = dateutil.parser.parse(value).date()
        elif output_type in ['NUMERIC', 'BIGNUMERIC', 'FLOAT64']:
            output_value = float(value)
        elif output_value == 'INT64':
            output_value = int(value)
        elif output_value == 'BOOLEAN':
            output_value = bool(value)
    return output_value


  def process(self,
              mutable_element: Dict
              ) -> Iterable[Dict]:
    try:
        output_element = {}
        for key, value in mutable_element.items():
            output_key = self.get_output_key(key)
            output_value = self.apply_output_type(output_key, value)
                    
            output_element[output_key] = output_value
        
        output_element['deleted'] = False
        output_element['last_updated'] = dt.datetime.now()
        self.correct_records_counter.inc()
        yield pvalue.TaggedOutput(AddMetadataDoFn.CORRECT_OUTPUT_TAG, output_element)

    except TypeError as err:
      self.wrong_records_counter.inc()
      msg = str(err)
      yield pvalue.TaggedOutput(AddMetadataDoFn.WRONG_OUTPUT_TAG, {'error': msg, 'line': mutable_element})