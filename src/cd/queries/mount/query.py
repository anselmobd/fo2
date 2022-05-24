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
        self.JoinRules = namedtuple('JoinRules', 'from_alias rules')
        self.JoinAlias = namedtuple('JoinAlias', 'table alias conditions')
        self.Condition = namedtuple('Condition', 'left test right')
        self.TemplateFields = namedtuple('TemplateFields', 'template fields')
        self.Template = namedtuple('Template', 'template')

    def get_join_rules(self, alias):
        if 'joined_to' in models.table[alias]:
            return [
                self.JoinRules(
                    from_alias=from_alias,
                    rules=models.table[alias]['joined_to'][from_alias],
                )
                for from_alias in self.table_aliases
                if from_alias in models.table[alias]['joined_to']
            ]

    def get_join_rule(self, alias):
        join_rules = self.get_join_rules(alias)
        if join_rules:
            return join_rules[0]

    def make_alias_field(self, alias, field):
        return self.AliasField(
            alias=alias,
            field=models.table[alias]['field'][field],
        )

    def join_conditions(self, alias, join_rule):
        conditions = []
        for left_rule in join_rule.rules:
            left_field = self.make_alias_field(alias, left_rule)

            right_rule = join_rule.rules[left_rule]
            if isinstance(right_rule, tuple):
                right_rule_fields = []
                if len(right_rule) == 2:
                    right_rule_field_aliases = right_rule[1]
                    if not isinstance(right_rule_field_aliases, tuple):
                        right_rule_field_aliases = (right_rule_field_aliases, )
                    for right_rule_field_alias in right_rule_field_aliases:
                        right_rule_fields.append(
                            self.make_alias_field(
                                join_rule.from_alias,
                                right_rule_field_alias,
                            )
                        )
                    right_field = self.TemplateFields(
                        template=right_rule[0],
                        fields=right_rule_fields
                    )
                else:
                    right_field = self.Template(
                        template=right_rule[0],
                    )

            else:
                right_field = self.make_alias_field(
                    join_rule.from_alias, right_rule)

            conditions.append(self.Condition(
                left=left_field,
                test="=",
                right=right_field,
            ))

        return conditions

    def joins_append(self, alias, join_rule):
        table_name = models.table[alias]['table']
        if join_rule:
            conditions = self.join_conditions(alias, join_rule)
        else:
            conditions = []
        self.joins.append(self.JoinAlias(
            table=table_name,
            alias=alias,
            conditions=conditions,
        ))

    def add_join(self, alias):
        join_rule = self.get_join_rule(alias)

        self.joins_append(alias, join_rule)

    def add_table(self, alias):
        table_name = models.table[alias]['table']
        self.froms.append(self.TableAlias(
            table=table_name,
            alias=alias,
        ))

    def add_alias(self, alias):
        if (
            alias not in self.table_aliases
            and alias in models.table
        ):
            if self.table_aliases:
                self.add_join(alias)
            else:
                self.add_table(alias)

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
            conditions = "\n AND ".join([
               self.mount_condition(condition)
               for condition in join.conditions
            ])
            if not conditions:
                conditions = "1=1"
            joins.append(
                f"JOIN {join.table} {join.alias}\n  ON {conditions}"
            )
        return "\n".join(joins)

    def add_filter(self, alias_field, value):
        table_alias, field_alias = alias_field.split('.')
        self.add_alias(table_alias)
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

    def mount_template_fields(self, template_fields):
        fields = []
        for alias_field in template_fields.fields:
            fields.append(self.mount_alias_field(alias_field))
        if fields:
            return template_fields.template.format(*fields)
        else:
            return template_fields.template

    def mount_alias_field_value(self, alias_field):
        if isinstance(alias_field, self.AliasField):
            return self.mount_alias_field(alias_field)
        if isinstance(alias_field, self.TemplateFields):
            return self.mount_template_fields(alias_field)
        if isinstance(alias_field, self.Template):
            return alias_field.template
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
        self.add_alias(table_alias)
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
