from collections import namedtuple
from pprint import pprint, pformat

from utils.functions.strings import noneifempty

from cd.queries.mount.relations import R


AliasField = namedtuple('AliasField', 'alias field')


class Field():

    def __init__(self, field):
        table_alias, field_alias = field.split('.')
        self.alias_field = AliasField(table_alias, field_alias)

    def structure(self):
        return self.alias_field

    def __repr__(self) -> str:
        return pformat(self.structure())


class Fields():

    def __init__(self):
        self.fields = []

    def add(self, field):
        self.fields.append(
            Field(field)
        )

    def structure(self):
        return self.fields

    def __repr__(self) -> str:
        return pformat(self.structure())


class Select():

    def __init__(self):
        self.fields = Fields()
        self.r = R()

    def structure(self):
        return {
            'fields': self.fields,
        }

    def __repr__(self) -> str:
        return pformat(self.structure())
