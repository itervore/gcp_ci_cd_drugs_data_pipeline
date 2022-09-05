import apache_beam as beam
import dateutil.parser


class DateCoder(beam.coders.Coder):
    def encode(self, date):
        return (f'{date}').encode('utf-8')

    def decode(self, str_date):
        return dateutil.parser.parse(str_date).date()

    def is_deterministic(self):
        return True