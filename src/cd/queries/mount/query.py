from collections import namedtuple
from pprint import pprint

from utils.functions.strings import noneifempty

from cd.queries.mount import models


class Query():
    def __init__(self):
        self.table_aliases = set()
        self.fields = []
        self.froms = []
        self.joins = []
        self.filters = []

        self.AliasField = namedtuple('AliasField', 'alias field')
        self.ValueAlias = namedtuple('ValueAlias', 'value alias')
        self.TableAlias = namedtuple('TableAlias', 'table alias')
        self.JoinAlias = namedtuple('JoinAlias', 'table alias conditions')
        self.Condition = namedtuple('Condition', 'left test right')

    def add_table(self, alias):
        if (
            alias not in self.table_aliases
            and alias in models.table
        ):
            table_name = models.table[alias]['table']

            join_rule = None
            for from_alias in self.table_aliases:
                join_key = f"{alias}<{from_alias}"
                if join_key in models.join:
                    join_rule = models.join[join_key]
                    break

            if join_rule:
                conditons = []
                for left_field_alias in join_rule:
                    left_field = self.AliasField(
                        alias=alias,
                        field=models.table[alias]['field'][left_field_alias],
                    )
                    right_field_alias = join_rule[left_field_alias]
                    right_field = self.AliasField(
                        alias=from_alias,
                        field=models.table[from_alias]['field'][right_field_alias],
                    )
                    conditons.append(self.Condition(
                        left=left_field,
                        test="=",
                        right=right_field,
                    ))
                self.joins.append(self.JoinAlias(
                    table=table_name,
                    alias=alias,
                    conditions=conditons,
                ))
            else:
                self.froms.append(self.TableAlias(
                    table=table_name,
                    alias=alias,
                ))
            self.table_aliases.add(alias)

    def mount_tables(self):
        if not self.froms:
            self.froms.append(self.TableAlias(
                table='dual',
                alias='',
            ))

        return ", ".join(
            f"{table.table} {table.alias}"
            for table in self.froms
        )

    def mount_joins(self):
        joins = []
        for join in self.joins:
            conditions = "\n AND".join([
               self.mount_condition(condition)
               for condition in join.conditions
            ])
            joins.append(
                f"JOIN {join.table} {join.alias}\n  ON {conditions}"
            )
        return "\n".join(joins)

    def add_filter(self, alias_field, value):
        table_alias, field_alias = alias_field.split('.')
        self.add_table(table_alias)
        table_field = models.table[table_alias]['field'][field_alias]
        self.filters.append(self.Condition(
            left=self.AliasField(
                alias=table_alias,
                field=table_field,
            ),
            test="=",
            right=value,
        ))

    def mount_alias_field(self, alias_field):
        return '.'.join(
            filter(
                None,
                [
                    noneifempty(alias_field.alias),
                    noneifempty(alias_field.field),
                ]
            )
        )

    def mount_alias_field_value(self, alias_field):
        if isinstance(alias_field, self.AliasField):
            return self.mount_alias_field(alias_field)
        else:
            if isinstance(alias_field, str):
                return f"'{alias_field}'"
            return alias_field

    def mount_condition(self, condition):
        left = self.mount_alias_field_value(condition.left)
        right = self.mount_alias_field_value(condition.right)
        return f"{left} {condition.test} {right}"

    def mount_where(self):
        where = "\n  AND ".join([
            self.mount_condition(filter)
            for filter in self.filters
        ])
        return f"WHERE {where}" if where else ""

    def add_select_field(self, alias_field):
        table_alias, field_alias = alias_field.split('.')
        self.add_table(table_alias)
        table_field = models.table[table_alias]['field'][field_alias]
        self.fields.append(self.ValueAlias(
            value=self.AliasField(
                alias=table_alias,
                field=table_field
            ),
            alias=field_alias,
        ))

    def mount_fields(self):
        if not self.fields:
            self.fields.append(self.ValueAlias(
                value=self.AliasField(
                    alias='',
                    field='CURRENT_TIMESTAMP'
                ),
                alias='',
            ))

        return "\n, ".join([
            f"{self.mount_alias_field_value(value_alias.value)} {value_alias.alias}"
            for value_alias in self.fields
        ])

    def sql(self):
        fields = self.mount_fields()
        tables = self.mount_tables()
        joins = self.mount_joins()
        where = self.mount_where()

        sql = "\n".join([
            "SELECT",
            f"  {fields}",
            f"FROM {tables}",
            f"{joins} -- joins",
            f"{where} -- where",
        ])

        return sql
