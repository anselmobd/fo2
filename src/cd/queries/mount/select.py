from collections import namedtuple
from pprint import pprint

from utils.functions.strings import noneifempty

from cd.queries.mount.relations import R


class Select():
    def __init__(self):
        self.table_aliases = []
        self.fields = []
        self.froms = []
        self.joins = []
        self.filters = []
        self.makes = set()

        self.r = R()

    def get_join_rules(self, alias):
        if 'joined_to' in self.r.table[alias]:
            return [
                self.JoinRules(
                    from_alias=from_alias,
                    rules=self.r.table[alias]['joined_to'][from_alias],
                )
                for from_alias in self.table_aliases
                if from_alias in self.r.table[alias]['joined_to']
            ]

    def get_join_rule(self, alias):
        join_rules = self.get_join_rules(alias)
        if join_rules:
            return join_rules[0]

    def make_alias_field(self, alias, field):
        return self.AliasField(
            alias=alias,
            field=self.r.table[alias]['field'][field],
        )

    def make_template_field(self, from_alias, right_rule):
        right_alias_fields = []
        if len(right_rule) > 1:
            right_rule_fields = right_rule[1:]
            if not isinstance(right_rule_fields, tuple):
                right_rule_fields = (right_rule_fields, )
            for right_rule_field in right_rule_fields:
                right_alias_fields.append(
                    self.make_alias_field(
                        from_alias,
                        right_rule_field,
                    )
                )
            right_field = self.TemplateFields(
                template=right_rule[0],
                fields=right_alias_fields
            )
        else:
            right_field = self.Template(
                template=right_rule[0],
            )
        return right_field

    def join_conditions(self, alias, join_rule):
        conditions = []
        for left_rule in join_rule.rules:
            left_field = self.make_alias_field(alias, left_rule)

            right_rule = join_rule.rules[left_rule]
            if isinstance(right_rule, tuple):
                right_field = self.make_template_field(
                    join_rule.from_alias, right_rule)
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
        table_name = self.r.table[alias]['table']
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

        self.add_conditions(alias)

    def add_conditions(self, alias):
        table_dict = self.r.table[alias]
        if 'condition' in table_dict:
            conditions = table_dict['condition']
            for key in conditions:
                self.filter_append(
                    alias,
                    key,
                    conditions[key],
                )

    def add_table(self, alias):
        table_name = self.r.table[alias]['table']
        self.froms.append(self.TableAlias(
            table=table_name,
            alias=alias,
        ))
        self.add_conditions(alias)

    def add_alias(self, alias):
        if (
            alias not in self.table_aliases
            and alias in self.r.table
        ):
            if self.table_aliases:
                self.add_join(alias)
            else:
                self.add_table(alias)

            self.table_aliases.append(alias)

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
        self.filter_append(table_alias, field_alias, value)

    def make_test_value(self, test_value):
        if isinstance(test_value, list):
            test=test_value[0]
            value=test_value[1]
        else:
            test='='
            value=test_value
        test_value_tuple = self.TestValue(
            test=test,
            value=value,
        )
        return test_value_tuple

    def filter_append(self, table_alias, field_alias, test_value):
        table_field = self.r.table[table_alias]['field'][field_alias]
        test_value_tuple = self.make_test_value(test_value)
        self.filters.append(self.Condition(
            left=self.AliasField(
                alias=table_alias,
                field=table_field,
            ),
            test=test_value_tuple.test,
            right=test_value_tuple.value,
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

    def get_alias_local(self, field_alias_local):
        if ' ' in field_alias_local:
            return field_alias_local.split(' ')
        else:
            return field_alias_local, field_alias_local

    def add_make(self, table, field, alias):
        if 'make' not in self.r.table[table]:
            return
        if field not in self.r.table[table]['make']:
            return
        self.makes.add(
            self.MakeField(
                table=table,
                field=field,
                alias=alias,
            )
        )

    def add_select_field(self, alias_field):
        table_alias, field_alias = alias_field.split('.')
        field_alias, alias_local = self.get_alias_local(field_alias)
        self.add_alias(table_alias)
        self.add_make(
            table_alias,
            field_alias,
            alias_local,
        )

        table_field = self.r.table[table_alias]['field'][field_alias]
        self.fields.append(self.ValueAlias(
            value=self.AliasField(
                alias=table_alias,
                field=table_field
            ),
            alias=alias_local,
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


    def apply_makes(self, data):
        for row in data:
            for make in self.makes:
                if make.alias not in row:
                    continue
                if 'make' not in self.r.table[make.table]:
                    continue
                if make.field not in self.r.table[make.table]['make']:
                    continue
                make_rule = self.r.table[
                    make.table]['make'][
                        make.field]
                row[make.alias] = make_rule[0](row[make.alias], make_rule[1])
