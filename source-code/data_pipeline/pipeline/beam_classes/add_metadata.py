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


class AddMetadataDoFn(DoFn):
  def __init__(self, header_to_bq_header, *unused_args, **unused_kwargs):
        self.header_to_bq_header = header_to_bq_header
        super()

  def process(self,
              mutable_element: Dict
              ) -> Iterable[Dict]:
    output_element = {}
    for key, value in mutable_element.items():
        if self.header_to_bq_header:
            output_key = self.header_to_bq_header.get(key, key)
        else : 
            output_key = key
        output_element[output_key] = value
    
    output_element['deleted'] = False
    output_element['last_updated'] = dt.datetime.now()
    yield output_element