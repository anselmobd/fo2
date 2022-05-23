from pprint import pprint

from cd.queries.mount import models


class Query():
    def __init__(self):
        self.from_tables = []
        self.tables_disponiveis = set()
        self.filter_list = []
        self.select_list = []

    def add_table(self, alias):
        if (
            alias not in self.tables_disponiveis
            and alias in models.table
        ):
            table_name = models.table[alias]['table']
            self.from_tables.append(f"{table_name} {alias}")
            self.tables_disponiveis.add(alias)

    def mount_tables(self):
        pprint(self.from_tables)
        return ", ".join(self.from_tables)

    def add_filter(self, alias_field, value):
        alias, field = alias_field.split('.')
        table_field = models.table[alias]['field'][field]
        self.filter_list.append([
            f"{alias}.{table_field}",
            "=",
            value,
        ])

    def mount_where(self):
        pprint(self.filter_list)
        wheres = []
        for filter in self.filter_list:
            wheres.append(f"{filter[0]} {filter[1]} {filter[2]}")
        return "\n AND ".join(wheres)

    def add_select_field(self, alias_field):
        table_alias, field_alias = alias_field.split('.')
        table_field = models.table[table_alias]['field'][field_alias]
        self.select_list.append(
            f"{table_alias}.{table_field} {field_alias}",
        )

    def mount_select_fields(self):
        pprint(self.select_list)
        return "\n, ".join(self.select_list)

    def sql(self):
        if not self.from_tables:
            self.from_tables = ['dual']
        tables = self.mount_tables()

        where = self.mount_where()
        where = f"WHERE {where}" if where else ""

        if not self.select_list:
            self.select_list = [1]
        select_fields = self.mount_select_fields()

        sql = "\n".join([
            "SELECT",
            f"  {select_fields}",
            f"FROM {tables}",
            f"{where}",
        ])
        print(sql)
        return sql
