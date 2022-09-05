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
from codecs import getencoder
from datetime import date
import apache_beam as beam  
from apache_beam.io.gcp import bigquery
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from pipeline.beam_classes.date_coder import DateCoder
from pipeline.beam_classes.write_json import TypeEncoder
from pipeline.beam_classes.list_combine import ListCombineFn


import logging

def run():
  parser = argparse.ArgumentParser()
  parser.add_argument("--bq-drug-table", required=True)
  parser.add_argument("--bq-clinicals-trials-table", required=True)
  parser.add_argument("--bq-pubmed-table", required=True)
  parser.add_argument("--results-bucket", required=True)
  parser.add_argument("--results-bq-table", required=True)
  parser.add_argument("--errors-bq-table", required=True)
  app_args, pipeline_args = parser.parse_known_args()

  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = True

  beam.coders.registry.register_coder(date, DateCoder)


  with beam.Pipeline(options=pipeline_options) as p:

    ### READ CLINICALS TRIALS

    clinicals_trials_main_input =  p | 'Reading side table : clinicals_trials' >> bigquery.ReadFromBigQuery(
      table=app_args.bq_clinicals_trials_table)

    drug_side_input =  p | 'Reading side table : drugs' >> bigquery.ReadFromBigQuery(
      table=app_args.bq_drug_table)

    def search_drug_in_title(article, drugs):
      list_tuple = []
      for drug in drugs:
        if drug.get('drug') and article.get('article_title'):
          drug_name = drug.get('drug').lower()
          lower_article_title = article.get('article_title').lower()
          if drug_name in lower_article_title:
            list_tuple.append((drug, article)) 
      return list_tuple

    def generate_elements(elements):
      for element in elements:
        yield element

    clinicals_trials_articles_by_drug = (clinicals_trials_main_input 
      | 'ProcessData : Search drug name in clinicals trials articles' >> beam.Map(
      search_drug_in_title, drugs=beam.pvalue.AsList(drug_side_input))
      | 'Flatten lists' >> beam.FlatMap(generate_elements)
       | 'ProcessData : Group drug' >> beam.GroupByKey()
      )

    def get_journal_from_articles(article):
      return (article.get('journal_title'), article.get('date'))

    clinicals_trials_journals_by_drug_step  = ( clinicals_trials_articles_by_drug
      | 'ProcessData : Retrieve journal from articles' >> beam.Map(
        lambda element : (element[0], element[1] | beam.Map(get_journal_from_articles  ))
        # beam.GroupBy('journal_title'))
      )
    )
      

    clinicals_trials_journals_by_drug = ( clinicals_trials_journals_by_drug_step
      | 'ProcessData : Group journals' >> beam.Map(
        lambda element : (element[0], element[1] | beam.GroupByKey()) )

      | 'ProcessData : Deduplicate date_mention' >> beam.Map(
          lambda element : (
            element[0],
            element[1] | beam.Map(
              lambda journal_tuple : 
              (journal_tuple[0],
              journal_tuple[1] | beam.Distinct())
              )
            )
          )
      )

    ### READ PUBMED
    pubmed_main_input =  p | '[pubmed] Reading side table : pubmed' >> bigquery.ReadFromBigQuery(
      table=app_args.bq_pubmed_table)

    pubmed_articles_by_drug = (pubmed_main_input 
      | '[pubmed] ProcessData : Search drug name in pubmed articles' >> beam.Map(
      search_drug_in_title, drugs=beam.pvalue.AsList(drug_side_input))
      | '[pubmed] Flatten lists' >> beam.FlatMap(generate_elements)
       | '[pubmed] ProcessData : Group drug' >> beam.GroupByKey()
      )

    pubmed_journals_by_drug_step  = ( pubmed_articles_by_drug
      | '[pubmed] ProcessData : Retrieve journal from articles' >> beam.Map(
        lambda element : (element[0], element[1] | beam.Map(get_journal_from_articles  ))
      )
    )

    pubmed_journals_by_drug = ( pubmed_journals_by_drug_step
      | '[pubmed] ProcessData : Group journals' >> beam.Map(
        lambda element : (element[0], element[1] | beam.GroupByKey()) )
      | '[pubmed] ProcessData : Deduplicate date_mention' >> beam.Map(
          lambda element : (
            element[0],
            element[1] | beam.Map(
              lambda journal_tuple : 
              (journal_tuple[0],
              journal_tuple[1] | beam.Distinct())
              )
            )
          )
      )

    ### Concatenate journals

    def make_flat_list(nestedlist):
      return [element for sublist in nestedlist for element in sublist]

    def merge_journals_dates(record):
      left_list_journal = make_flat_list(record[1]['pubmed_journals_by_drug'])
      right_list_journal=  make_flat_list(record[1]['clinicals_trials_journals_by_drug'])
      ouput_dict_journal = {jounal: list(set(mentions)) for (jounal, mentions) in right_list_journal }
      

      for left_journal in left_list_journal:
        is_created = False
        for right_journal in right_list_journal:
          if right_journal[0] == left_journal[0]:
            if ouput_dict_journal[right_journal[0]] is None:
                ouput_dict_journal[right_journal[0]] = []
            is_created = True
            ouput_dict_journal[right_journal[0]] = list(set(ouput_dict_journal[right_journal[0]] + right_journal[1] + left_journal[1]))
            ### merge dates
        if not is_created:
          ouput_dict_journal[left_journal[0]] = left_journal[1]
      list_output = list(ouput_dict_journal.items())
      return (record[0] , list_output )


    all_journals = (
        ({
        'pubmed_journals_by_drug' : pubmed_journals_by_drug,
        'clinicals_trials_journals_by_drug' : clinicals_trials_journals_by_drug
        })
       | '[journals] Merge' >> beam.CoGroupByKey() 
       | '[journals] Merges dates' >> beam.Map(merge_journals_dates)
      )

    def prepare_output(record):
      output_record= {}
      for key, value in record[0].items():
        if key == 'drug' :
          output_record['drug_name'] = value
          continue
        if key == 'atccode' :
          output_record['drug_atc_code'] = value
          continue
        if key in ['deleted', 'last_updated'] :
          continue

        output_record[key] = value

      journals = record[1]
      res_journals = []
      for journal in journals:
        res_journal = {}
        res_journal['journal_title'] = journal[0]
        dates = []
        for date_article in journal[1]:
          dates.append({'date': date_article})
        
        res_journal['date_mention'] = dates
        res_journals.append(res_journal)
      
      output_record['journals'] = res_journals

      output_record_pubmed_articles= []
      for article in record[2]:
        output_article = {}
        for key, value in article.items():

          if key in ['deleted', 'last_updated'] :
            continue
          output_article[key] = value
        output_record_pubmed_articles.append(output_article)
      output_record['pubmed_articles'] = output_record_pubmed_articles

      output_record_clinical_trials_articles= []
      for article in record[3]:
        output_article = {}
        for key, value in article.items():
          if key in ['deleted', 'last_updated'] :
            continue
          output_article[key] = value
        output_record_clinical_trials_articles.append(output_article)
        
      output_record['clinical_trials_articles'] = output_record_clinical_trials_articles


      return output_record

    graph_drug = (
      (
        {
        'journals' : all_journals,
        'pubmed_articles' : pubmed_articles_by_drug,
        'clinicals_trials_articles': clinicals_trials_articles_by_drug
        }
      ) | '[graph step] Merge' >> beam.CoGroupByKey()
        | '[graph]  Flatten record' >> beam.Map(lambda record : 
        (record[0], (make_flat_list(record[1]['journals']) ), (make_flat_list(record[1]['pubmed_articles']) ), (make_flat_list(record[1]['clinicals_trials_articles']) )))
        | '[graph] Format record' >> beam.Map(prepare_output)
    )

    graph_drug | "Write results to BigQuery" >> beam.io.WriteToBigQuery(
      table=app_args.results_bq_table,
      create_disposition=bigquery.BigQueryDisposition.CREATE_NEVER,
      write_disposition=bigquery.BigQueryDisposition.WRITE_TRUNCATE)


    unique_graph_drug = graph_drug | 'Combine results' >> beam.CombineGlobally(ListCombineFn())
    json_graph_drug = (unique_graph_drug | 'JSON format' >> beam.Map(json.dumps, cls=TypeEncoder) )

    json_graph_drug | 'Write Output' >> beam.io.WriteToText(app_args.results_bucket + "/graph_drug_mention", file_name_suffix=".json", shard_name_template='')



if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
