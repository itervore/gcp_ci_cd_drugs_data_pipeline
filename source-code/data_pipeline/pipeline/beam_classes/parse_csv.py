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
from collections import namedtuple

from typing import Dict
from apache_beam import DoFn, pvalue
from apache_beam.metrics import Metrics
import re


class ParseCSVDoFn(DoFn):
  CORRECT_OUTPUT_TAG = 'accommodations'
  WRONG_OUTPUT_TAG = 'parse_errors'

  def __init__(self, header_line: str, sep: str):
    """ Parse the CSV data and create a PCollection of Accommodation.
    Args:
        header_line: The header line used in the CSV line, it will be ignored by the parser.
    """
    self._header_line = header_line
    self.sep = sep
    

    # Metrics to report the number of records
    self.input_records_counter = Metrics.counter("ParseCSVDoFn", 'input_records')
    self.correct_records_counter = Metrics.counter("ParseCSVDoFn", 'correct_records')
    self.wrong_records_counter = Metrics.counter("ParseCSVDoFn", 'wrong_records')

  def create_multiple_field_str(self, tmp_str, in_str, field):
    multipart_str_is_completed = False

    # Field is double quoted:
    if not in_str and field.count('"') == 2 :
        in_str = False
        tmp_str = ""
        return tmp_str, in_str, multipart_str_is_completed
    
    # Field is not part of a multiple field str
    if not in_str and field.count('"') == 0 :
        in_str = False
        tmp_str = ""
        return tmp_str, in_str, multipart_str_is_completed
    
    # Field is the beginning of a multiple field str
    if not in_str and field.count('"') == 1 :
        in_str = True
        tmp_str = field.strip('"')+','
        return tmp_str, in_str, multipart_str_is_completed

    # Field is the end part of a multiple field str
    if in_str and field.count('"') == 1 :
        in_str = False
        tmp_str = tmp_str + field.strip('"')
        multipart_str_is_completed = True
        return tmp_str, in_str, multipart_str_is_completed

    # Field is part of a multiple field str
    if in_str and field.count('"') == 0 :
        in_str = True
        tmp_str = tmp_str + field.strip('"')+','
        return tmp_str, in_str, multipart_str_is_completed

    raise( Exception(f"Too many double quote for a csv in the field: {field}"))
    
  def process(self, element: str):
    self.input_records_counter.inc()
    Record = namedtuple('Record', self._header_line.split(self.sep))
    # We have two outputs: one for well formed input lines, and another one with potential parsing errors
    # (the parsing error output will be written to a different BigQuery table)
    try:
      # ignore header row
      if element != self._header_line:
    
            line = element.split(self.sep)
            output_elements = []
            tmp_str = ""
            in_str = False
            for field in line:
                tmp_str, in_str, multipart_str_is_completed = self.create_multiple_field_str(tmp_str, in_str, field)
                if multipart_str_is_completed:
                    field = tmp_str
                if in_str:
                    continue

                if(len(field) > 0):
                    cleaned_field = re.sub(r'\\x..',r'', field) # REMOVE ALL \x char
                
                
                cleaned_field = cleaned_field.strip()
                cleaned_field = cleaned_field.strip('"')      
                output_elements.append(cleaned_field)  
            record: Dict =  Record(*output_elements)._asdict()
        
            self.correct_records_counter.inc()
            yield pvalue.TaggedOutput(ParseCSVDoFn.CORRECT_OUTPUT_TAG, record)
    except TypeError as err:
      self.wrong_records_counter.inc()
      msg = str(err)
      yield pvalue.TaggedOutput(ParseCSVDoFn.WRONG_OUTPUT_TAG, {'error': msg, 'line': element})