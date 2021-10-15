#!/usr/bin/env python

import os
import pandas as pd
import sqlite3 as sq
import sys
from dbfread import DBF, FieldParser
from pprint import pprint


class DupProcess():

    def __init__(self, file_name=None, action=None, rec_slice=None, fields=None) -> None:
        self.file_name = file_name
        self.action = action
        self.rec_slice = rec_slice
        self.fields = fields

        self.load()
        self.action()

    @property
    def file_name(self):
        return self.__file_name
      
    @file_name.setter
    def file_name(self, val):
        if val is None or not os.path.isfile(val):
            raise Exception('Primeiro parâmetro deve ser o nome do DBF')
        self.__file_name = val

    def nothing(self):
        pass

    @property
    def action(self):
        return self.__action
      
    @action.setter
    def action(self, val=None):
        if val is None or val == 'print':
            self.__action = self.print
        elif val == 'to_sqlite':
            self.__action = self.to_sqlite
        else:
            self.__action = self.nothing
  
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

    def load(self):
        self.dbf = pd.DataFrame(
            DBF(
                self.file_name,
                encoding='cp850',
                lowernames=True,
                parserclass=self.MyFieldParser,
            )
        )

    def print(self):
        result = self.dbf[self.rec_slice][self.fields if self.fields else self.dbf.columns]
        print(result.to_string(index=False))      

    def to_sqlite(self):
        sql_data = 'dbf.sqlite'
        conn = sq.connect(sql_data)
        cur = conn.cursor()
        cur.execute('''DROP TABLE IF EXISTS DBF''')
        self.dbf.to_sql('DBF', conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()

if __name__ == '__main__':
    dp = DupProcess(*sys.argv[1:])
