
import apache_beam as beam

class ListCombineFn(beam.CombineFn):
    def create_accumulator(self):
        return []

    def add_input(self, accumulator, input):
        accumulator.append(input)
        return accumulator

    def merge_accumulators(self, accumulators):
        merged = []
        for accum in accumulators:
            merged += accum
        return merged

    def extract_output(self, accumulator):
        return accumulator