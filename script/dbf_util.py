#!/usr/bin/env python

import argparse
from datetime import date
import os
import pandas as pd
import sqlite3 as sq
from dbfread import DBF, FieldParser
from pprint import pprint


class DbfUtil():

    def __init__(self, argv=None) -> None:
        self.dbf = None
        self.parseArgs(argv)

    @property
    def file_name(self):
        return self.__file_name
      
    @file_name.setter
    def file_name(self, val):
        self.__file_name = val

    @property
    def action(self):
        return self.__action
      
    @action.setter
    def action(self, val):
        self.__action = val
  
    def int_def(self, val, default):
        try:
            return int(val)
        except ValueError:
            return default

    @property
    def rec_slice(self):
        return self.__rec_slice
      
    @rec_slice.setter
    def rec_slice(self, val):
        if val is None:
            val = (0,-1)
        if isinstance(val, str):
            val = tuple(
                self.int_def(v, None)
                for v in val.strip(" ()").split(',')
            )
        if not isinstance(val, tuple):
            val = (val, )
        self.__rec_slice = slice(*val)

    @property
    def fields(self):
        return self.__fields
      
    @fields.setter
    def fields(self, val):
        if val is None:
            val = []
        if isinstance(val, str):
            val = (
                v.strip(" ")
                for v in val.strip(" ()").split(',')
            )
        self.__fields = val
  
    class MyFieldParser(FieldParser):
        def parse(self, field, data):
            try:
                return FieldParser.parse(self, field, data)
            except Exception:
                return None

    def mystrip(self, s):
        return s.strip()

    def filter_dup(self):
        if self.args.filter_dup:
            self.dbf.drop(
                self.dbf[
                    (self.dbf.d_dupnum == '0000000') |
                    (self.dbf.d_dupnum.map(self.mystrip).map(len) < 6)
                ].index,
                inplace=True
            )
            self.dbf.drop_duplicates(
                subset='d_dupnum', keep='last', inplace=True)

    def load(self):
        if self.dbf is None:
            self.dbf = pd.DataFrame(
                DBF(
                    self.file_name,
                    encoding='cp850',
                    lowernames=True,
                    parserclass=self.MyFieldParser,
                )
            )
            self.filter_dup()
            self.dbf = self.dbf[self.rec_slice][self.fields if self.fields else self.dbf.columns]

    def print(self):
        print(self.dbf.to_string(index=False))      

    def val2sql(self, val):
        if isinstance(val, str):
            return f"'{val}'"
        elif isinstance(val, date):
            return f"'{val.ctime()}'"
        elif val is None:
            return 'NULL'
        else:
            return str(val)

    def insert_update(self, table, conn, keys, data_iter):
        if table.schema:
            table_name = '{}.{}'.format(table.schema, table.name)
        else:
            table_name = table.name

        columns = ', '.join(k for k in keys)

        pk_position = keys.index(self.pk_field)

        for data in data_iter:
            row = [self.val2sql(v) for v in data]

            values = ', '. join(row)
            update = ', '. join([
                f"{kv[0]} = {kv[1]}"
                for kv in zip(keys, row)
            ])

            sql = f'''
                select
                    {self.pk_field}
                from {table_name}
                where {self.pk_field} = {data[pk_position]}
            '''
            conn.execute(sql)
            rows = conn.fetchall()
            if len(rows) == 0:
                sql = f'''
                    insert into {table_name} ({columns})
                    values ({values})
                '''
            else:
                sql = f'''
                    UPDATE {table_name}
                    SET {update}
                    where {self.pk_field} = {data[pk_position]}
                '''
            print(sql)
            conn.execute(sql)
            return

    def to_sqlite(self):
        self.pk_field = 'd_dupnum'
        sql_data = 'dbf.sqlite'
        conn = sq.connect(sql_data)
        if self.drop:
            cur = conn.cursor()
            cur.execute(f"DROP TABLE IF EXISTS {self.table_name}")
            conn.commit()
        self.dbf.to_sql(
            self.table_name,
            conn,
            if_exists='append',
            index=False,
            method=self.method,
        )
        conn.commit()
        conn.close()

    def set_action(self):
        if self.args.print:
            self.action = self.print
        elif self.args.table:
            self.action = self.to_sqlite
            self.table_name = self.args.table
            self.drop = not self.args.no_drop
            if self.args.insert_update:
                self.method = self.insert_update
            else:
                self.method = None
  
    def dbf_file(self, astring):
        if not os.path.isfile(astring):
            raise ValueError
        return astring

    def parseArgs(self, argv=None):
        parser = argparse.ArgumentParser(
            description='Util to process DBF',
            epilog="(c) Oxigenai",
            formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument(
            "file_name",
            type=self.dbf_file,
            help='DBF file name')

        action_group = parser.add_mutually_exclusive_group(
            required=True)

        action_group.add_argument(
            "-p", "--print",
            action="store_true",
            default=False,
            help='Print DBF data frame')

        action_group.add_argument(
            "-t", "--table",
            type=str,
            help='Name of table in SQLite to receive DBF data frame')

        parser.add_argument(
            "-s", "--slice",
            type=str,
            help='Slice of records to process')

        parser.add_argument(
            "-f", "--fields",
            type=str,
            help='List of fields to process')

        parser.add_argument(
            "--filter-dup",
            action="store_true",
            default=False,
            help='Filtra d_dupnum fora do padrão')

        parser.add_argument(
            "--no-drop",
            action="store_true",
            default=False,
            help='Não apaga a tabela antes de inserir dados')

        parser.add_argument(
            "--insert-update",
            action="store_true",
            default=False,
            help='Utiliza método insert_update no to_sql')

        parser.add_argument(
            "-v", "--verbosity", action="count", default=0,
            help="Increase output verbosity")

        self.args = parser.parse_args(argv)

        self.file_name = self.args.file_name
        self.set_action()
        self.rec_slice = self.args.slice
        self.fields = self.args.fields

    def run(self):
        self.load()
        self.action()


def main():
    du = DbfUtil()
    du.run()


if __name__ == '__main__':
    main()
