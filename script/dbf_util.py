#!/usr/bin/env python

import argparse
import os
import pandas as pd
import sqlite3 as sq
from dbfread import DBF, FieldParser
from pprint import pprint


class DbfUtil():

    def __init__(self) -> None:
        self.dbf = None
        self.parseArgs()

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

    def set_action(self):
        if self.args.print:
            self.action = self.print
        elif self.args.to_sqlite:
            self.action = self.to_sqlite
  
    def dbf_file(self, astring):
        if not os.path.isfile(astring):
            raise ValueError  # or TypeError, or `argparse.ArgumentTypeError
        return astring

    def parseArgs(self):
        parser = argparse.ArgumentParser(
            description='Util to process DBF',
            epilog="(c) Oxigenai",
            formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument(
            "file_name",
            type=self.dbf_file,
            help='DBF file name')

        group = parser.add_mutually_exclusive_group(
            required=True)

        group.add_argument(
            "-p", "--print",
            action="store_true",
            default=False,
            help='print DBF data frame')

        group.add_argument(
            "-t", "--to_sqlite",
            action="store_true",
            default=False,
            help='write DBF data frame to SQLite')

        parser.add_argument(
            "-s", "--slice",
            type=str,
            help='slice of records to process')

        parser.add_argument(
            "-f", "--fields",
            type=str,
            help='list of fields to process')

        parser.add_argument(
            "-v", "--verbosity", action="count", default=0,
            help="increase output verbosity")

        self.args = parser.parse_args()

        self.file_name = self.args.file_name
        self.set_action()
        self.rec_slice = self.args.slice
        self.fields = self.args.fields

    def run(self):
        self.load()
        self.action()


if __name__ == '__main__':
    du = DbfUtil()
    du.run()
