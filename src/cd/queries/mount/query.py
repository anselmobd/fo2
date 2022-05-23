from pprint import pprint

from cd.queries.mount import models


class Query():
    def __init__(self):
        # property
        self._table = None

        # outras
        self.from_table = None
        self.tables_disponiveis = set()
        self.filter_list = []
        self.select_list = []

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, alias):
        if self._table != alias:
            if alias in models.table:
                table_name = models.table[alias]['table']
                self.from_table = f"{table_name} {alias}"
                self._table = alias
                self.tables_disponiveis.add(alias)

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
        teble_alias, field_alias = alias_field.split('.')
        table_field = models.table[teble_alias]['field'][field_alias]
        self.select_list.append(
            f"{teble_alias}.{table_field} {field_alias}",
        )

    def mount_select_fields(self):
        pprint(self.select_list)
        return "\n, ".join(self.select_list)

    def sql(self):
        if not self.from_table:
            self.from_table = 'dual'

        where = self.mount_where()
        where = f"WHERE {where}" if where else ""

        if not self.select_list:
            self.select_list = [1]
        select_fields = self.mount_select_fields()

        sql = "\n".join([
            "SELECT",
            f"  {select_fields}",
            f"FROM {self.from_table}",
            f"{where}",
        ])
        print(sql)
        return sql
