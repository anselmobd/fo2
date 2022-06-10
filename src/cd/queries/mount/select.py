import re
from collections import namedtuple
from pprint import pprint, pformat

from utils.functions.strings import noneifempty

from cd.queries.mount.relations import R


# fields: [ValueAlias, ...]
# tables: [From, Join, ...]
Statement = namedtuple('Statement', 'fields tables')
# table_alias: alias/código da tabela; e
# field: código do field na tabela
AliasField = namedtuple('AliasField', 'table_alias field')
# value: AliasField, literal ou outra coisa; e
# alias: do value
ValueAlias = namedtuple('ValueAlias', 'value alias')
# alias: da tabela
From = namedtuple('From', 'alias')
# alias: da tabela
Join = namedtuple('Join', 'alias condition')


class Base():

    def structure(self):
        pass

    def __repr__(self) -> str:
        return pformat(self.structure())


class Field(Base):

    def __init__(self, field):
        partes = re.split(r"([\. ])", field.strip())
        if len(partes) > 5:
            raise ValueError("Field mal definido")

        try:
            pos_dot = partes.index('.')
            table_alias = partes[pos_dot-1]
            partes = partes[pos_dot+1:]
        except ValueError:
            table_alias = None

        try:
            pos_dot = partes.index(' ')
            local_alias = partes[-1]
        except ValueError:
            local_alias = None

        field_alias = partes[0]

        self.field = ValueAlias(
            AliasField(
                table_alias,
                field_alias,
            ),
            local_alias,
        )

    def set_table_alias(self, table_alias):
        self.field = ValueAlias(
            AliasField(
                table_alias,
                self.field.value.field,
            ),
            self.field.alias,
        )

    def structure(self):
        return self.field


class Fields(Base):

    def __init__(self):
        self.fields = []

    def add(self, field):
        field_obj = Field(field)
        self.fields.append(field_obj)
        return field_obj

    def structure(self):
        return self.fields


class Tables(Base):

    def __init__(self):
        self.tables = []

    def add(self, table_alias):
        if self.tables:
            table_obj = Join(
                table_alias,
                None
            )
        else:
            table_obj = From(
                table_alias,
            )
        self.tables.append(table_obj)
        return table_obj

    def structure(self):
        return self.tables


class Select(Base):

    def __init__(self):
        self.statement = Statement(
            Fields(),
            Tables(),
        )
        self.r = R()

    def add_table(self, table_alias):
        self.statement.tables.add(table_alias)

    def add_from(self, table_alias):
        self.add_table(table_alias)

    def add_field(self, field):
        field_obj = self.statement.fields.add(field)
        table_alias = field_obj.field.value.table_alias
        if table_alias is None:
            table_alias = self.statement.tables.tables[0].alias
            field_obj.set_table_alias(table_alias)
        else:    
            self.add_table(table_alias)

    def structure(self):
        return self.statement
