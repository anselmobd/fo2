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

    def param_ok(self):
        if self.ano is None or \
                self.mes is None or \
                self._refs is None:
            raise ValueError(
                "Refs, ano e mes pós inventário devem ser informados")

    def get_invent(self):
        self.param_ok()
        count = len(self._refs['data'])
        for i, values in enumerate(self._refs['data']):
            row = dict(zip(self._refs['keys'], values))
            print('({}/{}) {}'.format(i+1, count, row['REFERENCIA']))
            self.get_ref_invent(row['REFERENCIA'])

    def get_ref_invent(self, ref):
        sql = """
            SELECT
              e.NIVEL_ESTRUTURA
            , e.GRUPO_ESTRUTURA
            , e.SUBGRUPO_ESTRUTURA
            , e.ITEM_ESTRUTURA
            , e.CODIGO_DEPOSITO
            , e.data_movimento
            , e.sequencia_ficha
            , e.saldo_fisico
            , e.saldo_financeiro
            , e.preco_medio_unitario
            FROM estq_310 e
            JOIN (
              SELECT
                e.NIVEL_ESTRUTURA
              , e.GRUPO_ESTRUTURA
              , e.SUBGRUPO_ESTRUTURA
              , e.ITEM_ESTRUTURA
              , e.CODIGO_DEPOSITO
              , edt.DATA_BUSCA
              , max(e.SEQUENCIA_FICHA) SEQUENCIA_BUSCA
              FROM estq_310 e
              JOIN (
                SELECT
                  e.NIVEL_ESTRUTURA
                , e.GRUPO_ESTRUTURA
                , e.SUBGRUPO_ESTRUTURA
                , e.ITEM_ESTRUTURA
                , e.CODIGO_DEPOSITO
                , max(e.DATA_MOVIMENTO) DATA_BUSCA
                FROM estq_310 e
                WHERE e.NIVEL_ESTRUTURA = 9
                  AND e.GRUPO_ESTRUTURA = :referencia
                  AND e.DATA_MOVIMENTO < TO_DATE('2019-01-01','YYYY-MM-DD')
                GROUP BY
                  e.NIVEL_ESTRUTURA
                , e.GRUPO_ESTRUTURA
                , e.SUBGRUPO_ESTRUTURA
                , e.ITEM_ESTRUTURA
                , e.CODIGO_DEPOSITO
              ) edt
                ON edt.codigo_deposito    = e.codigo_deposito
               and edt.nivel_estrutura    = e.nivel_estrutura
               and edt.grupo_estrutura    = e.grupo_estrutura
               and edt.subgrupo_estrutura = e.subgrupo_estrutura
               and edt.item_estrutura     = e.item_estrutura
               and edt.data_busca         = e.data_movimento
              group by
                e.codigo_deposito
              , e.nivel_estrutura
              , e.grupo_estrutura
              , e.subgrupo_estrutura
              , e.item_estrutura
              , edt.data_busca
            ) eseq
              ON eseq.codigo_deposito    = e.codigo_deposito
             and eseq.nivel_estrutura    = e.nivel_estrutura
             and eseq.grupo_estrutura    = e.grupo_estrutura
             and eseq.subgrupo_estrutura = e.subgrupo_estrutura
             and eseq.item_estrutura     = e.item_estrutura
             and eseq.data_busca         = e.data_movimento
             and eseq.SEQUENCIA_BUSCA    = e.SEQUENCIA_FICHA
        """
        ref_invent = self._ora.execute(sql, referencia=ref)

        nkeys = len(ref_invent['keys'])
        mask = self.make_csv_mask(nkeys)
        for values in ref_invent['data']:
            print(mask.format(*values))

    def make_csv_mask(self, nkeys):
        sep = ''
        result = ''
        for _ in range(nkeys):
            result += sep + '"{}"'
            sep = ';'
        return result


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
