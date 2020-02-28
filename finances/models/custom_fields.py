import json

from django.db.models import TextField


class SimpleJsonField(TextField):
    description = 'Simple field to store json as text in db'

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return json.loads(value)

    def to_python(self, value):
        if value is None or isinstance(value, dict) or isinstance(value, list):
            return value
        else:
            return json.loads(value)

    def get_prep_value(self, value):
        return json.dumps(value)