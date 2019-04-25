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

        result = {
            'keys': [f[0] for f in self.cursor.description],
            'data': self.cursor.fetchall(),
        }
        return result

    def close(self):
        try:
            if self.cursor is not None:
                self.cursor.close()
            self.con.close()
        except cx_Oracle.DatabaseError as e:
            print('[Closing error] {}'.format(e))
            sys.exit(4)


class Inventario:

    def __init__(self, ora):
        self._ora = ora
        self._nivel = 9
        self._refs = None
        self._ano = None
        self._mes = None

    @property
    def nivel(self):
        return self._nivel

    @nivel.setter
    def nivel(self, value):
        self._nivel = value

    @property
    def ano(self):
        return self._ano

    @ano.setter
    def ano(self, value):
        self._ano = value

    @property
    def mes(self):
        return self._mes

    @mes.setter
    def mes(self, value):
        self._mes = value

    def get_refs(self, nivel=None, rownum=None):
        if nivel is None:
            nivel = self.nivel
        else:
            self.nivel = nivel

        rownum_filter = ''
        if rownum is not None:
            rownum_filter = 'AND rownum <= {}'.format(rownum)

        sql = """
            SELECT
              r.REFERENCIA
            FROM BASI_030 r
            WHERE r.NIVEL_ESTRUTURA = :nivel
              AND r.REFERENCIA NOT LIKE 'DV%'
              {rownum_filter} -- rownum_filter
            ORDER BY
              r.REFERENCIA
        """.format(
            rownum_filter=rownum_filter
        )
        self._refs = self._ora.execute(sql, nivel=self.nivel)
        # pprint(self._refs['data'])
        # pprint(self._refs['keys'])

    def param_ok(self):
        if self.ano is None or \
                self.mes is None or \
                self._refs is None:
            raise ValueError(
                "Refs, ano e mes pós inventário devem ser informados")

    def get_invent(self):
        self.param_ok()
        for values in self._refs['data']:
            row = dict(zip(self._refs['keys'], values))
            print(row['REFERENCIA'])


if __name__ == '__main__':
    ora = Oracle()
    ora.connect()

    inv = Inventario(ora)
    inv.nivel = 9
    inv.get_refs(rownum=5)

    inv.ano = 2019
    inv.mes = 1
    inv.get_invent()

    ora.close()
