#!/usr/bin/env python

import sys
import cx_Oracle
from pprint import pprint


class Oracle:

    def __init__(self):
        self.username = 'systextil'
        self.password = 'oracle'
        self.hostname = 'localhost'
        self.port = 26521
        self.servicename = 'XE'
        self.schema = 'SYSTEXTIL'

    def connect(self):
        try:
            self.con = cx_Oracle.connect(
                self.username,
                self.password,
                '{}:{}/{}'.format(
                    self.hostname,
                    self.port,
                    self.servicename
                )
            )
        except cx_Oracle.DatabaseError as e:
            print('[Connection error] {}'.format(e))
            sys.exit(1)

        self.con.current_schema = self.schema
        self.cursor = self.con.cursor()

        try:
            self.cursor.execute(
                'select USERNAME from SYS.ALL_USERS')
        except cx_Oracle.DatabaseError as e:
            print('[Schema {} error] {}'.format(self.schema, e))
            sys.exit(2)

    def execute(self, sql, **xargs):
        try:
            if len(xargs.keys()) == 0:
                self.cursor.execute(sql)
            else:
                self.cursor.execute(sql, xargs)
        except cx_Oracle.DatabaseError as e:
            print('[Execute error] {}'.format(e))
            sys.exit(3)

        return self.cursor.fetchall()


    def close(self):
        try:
            if self.cursor is not None:
                self.cursor.close()
            self.con.close()
        except cx_Oracle.DatabaseError as e:
            print('[Closing error] {}'.format(e))
            sys.exit(4)

if __name__ == '__main__':
    ora = Oracle()
    ora.connect()

    sql = """
        SELECT
          u.USUARIO
        FROM HDOC_030 u
        WHERE u.CODIGO_USUARIO = :codigo
    """
    data = ora.execute(sql, codigo=99101)

    pprint(data)

    ora.close()
