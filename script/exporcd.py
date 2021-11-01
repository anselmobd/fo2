#!/usr/bin/env python

import pandas as pd
import psycopg2
import sys
import timeit
from collections import namedtuple
from pprint import pprint

from db_password import (
    DBPASS,
)


def rows_to_dict_list_lower(cursor):
    columns = [i[0].lower() for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def rows_to_namedtuple(cursor):
    Row = namedtuple('Row', [i[0].lower() for i in cursor.description])
    return [Row(*row) for row in cursor]


class ExpCD():

    def conecta(self):
        self.conn = psycopg2.connect(
            host="localhost",
            port=25432,
            database="tussor_fo2_production",
            user="tussor_fo2",
            password=DBPASS,
        )
        self.cursor = self.conn.cursor()
    
    def get_locais_sql(self):
        return """
            select distinct
              l.local
            from fo2_cd_lote l
            left join fo2_cd_endereco_disponivel ed 
              on ed.disponivel
             and l.local like (ed.inicio || '%')
            left join fo2_cd_endereco_disponivel ned 
              on ed.disponivel is not null
             and (not ned.disponivel)
             and ned.inicio like (ed.inicio || '%')
             and l.local like (ned.inicio || '%')
            where l.local is not null
              and l.local <> ''
              and ed.disponivel is not null
              and ned.disponivel is null
            order by
              l.local
        """

    def get_locais(self):
        self.cursor.execute(self.get_locais_sql())

    def print_cursor_fetchall(self):
        self.get_locais()
        data = self.cursor.fetchall()
        pprint(data[:10])
        print(data[0][0])
        print('fetchall', sys.getsizeof(data))

    def print_cursor_dict(self):
        self.get_locais()
        data = rows_to_dict_list_lower(self.cursor)
        pprint(data[:10])
        print(data[0]['local'])
        print('dict', sys.getsizeof(data))

    def print_cursor_namedtuple(self):
        self.get_locais()
        data = rows_to_namedtuple(self.cursor)
        pprint(data[:10])
        print(data[0].local)
        print('namedtuple', sys.getsizeof(data))

    def print_cursor_pd(self):
        data = pd.read_sql_query(
            self.get_locais_sql(), self.conn
        )
        pprint(data[:10])
        pprint(data[0:1])
        print('pd', sys.getsizeof(data))


def get_timeit(func):
    starttime = timeit.default_timer()
    func()
    print("Timeit:", timeit.default_timer() - starttime)


def main():
    ecd = ExpCD()
    ecd.conecta()

    get_timeit(ecd.print_cursor_fetchall)

    get_timeit(ecd.print_cursor_dict)

    get_timeit(ecd.print_cursor_namedtuple)

    get_timeit(ecd.print_cursor_pd)


if __name__ == '__main__':
    main()
