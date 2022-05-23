from pprint import pprint

from cd.queries.mount import models


class Query():
    def __init__(self):
        self.from_tables = []
        self.tables_disponiveis = set()
        self.filter_list = []
        self.select_list = {}
        self.join_list = []

    def add_table(self, alias):
        if (
            alias not in self.tables_disponiveis
            and alias in models.table
        ):
            print('add_table', alias)
            table_name = models.table[alias]['table']

            join_rule = None
            for from_table in self.tables_disponiveis:
                join_key = f"{alias}<{from_table}"
                pprint(models.join)
                if join_key in models.join:
                    join_rule = models.join[join_key]
                    break

            pprint(join_rule)
            if join_rule:
                join_on_list = []
                for join_field_alias in join_rule:
                    join_field = models.table[alias]['field'][join_field_alias]
                    from_field_alias = join_rule[join_field_alias]
                    table_field = models.table[from_table]['field'][from_field_alias]
                    join_on_list.append([
                        join_field,
                        "=",
                        table_field,
                    ])
                self.join_list.append([
                    table_name,
                    alias,
                    from_table,
                    join_on_list,
                ])
            else:
                self.from_tables.append([
                    table_name,
                    alias,
                ])
            self.tables_disponiveis.add(alias)

    def mount_tables(self):
        if not self.from_tables:
            self.from_tables = ['dual', '']

        pprint(self.from_tables)
        return ", ".join(
            f"{table[0]} {table[1]}"
            for table in self.from_tables
        )

    def mount_joins(self):
        pprint(self.join_list)
        joins = []
        for join_parms in self.join_list:
            join_on_list = join_parms[3]
            join_on = "\n AND".join([
               f"{join_parms[1]}.{parm[0]} {parm[1]} {join_parms[2]}.{parm[2]}"
               for parm in join_on_list
            ])
            joins.append(
                f"JOIN {join_parms[0]} {join_parms[1]} \n  ON {join_on}"
            )
        return "\n".join(joins)

    def add_filter(self, alias_field, value):
        table_alias, field_alias = alias_field.split('.')
        self.add_table(table_alias)
        table_field = models.table[table_alias]['field'][field_alias]
        self.filter_list.append([
            f"{table_alias}.{table_field}",
            "=",
            value,
        ])

    def mount_where(self):
        pprint(self.filter_list)
        wheres = []
        for filter in self.filter_list:
            if isinstance(filter[2], str):
                value = f"'{filter[2]}'"
            else:
                value = filter[2]
            wheres.append(f"{filter[0]} {filter[1]} {value}")
        where = "\n  AND ".join(wheres)
        where = f"WHERE {where}" if where else ""
        return where

    def add_select_field(self, alias_field):
        table_alias, field_alias = alias_field.split('.')
        self.add_table(table_alias)
        table_field = models.table[table_alias]['field'][field_alias]
        self.select_list[field_alias] = [
            table_alias,
            table_field,
        ]

    def mount_select_fields(self):
        if not self.select_list:
            self.select_list = ['CURRENT_TIMESTAMP']

        pprint(self.select_list)
        return "\n, ".join([
            f"{self.select_list[alias][0]}.{self.select_list[alias][1]} {alias}"
            for alias in self.select_list
        ])

    def sql(self):
        select_fields = self.mount_select_fields()
        tables = self.mount_tables()
        joins = self.mount_joins()
        where = self.mount_where()

        sql = "\n".join([
            "SELECT",
            f"  {select_fields}",
            f"FROM {tables}",
            f"{joins} -- joins",
            f"{where} -- where",
        ])
        print(sql)
        return sql
