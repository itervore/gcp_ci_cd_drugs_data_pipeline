

from datetime import date
import json


class TypeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, date):
            return str(obj)
        return json.JSONEncoder.default(self, obj)