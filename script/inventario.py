#!/usr/bin/env python

import sys
import cx_Oracle
from pprint import pprint
import locale
import argparse


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
        # inicializado via parâmetros
        self._ora = ora

        # inicialização fixa
        self._print_fields = True

        # valor default
        self._nivel = 9

        # valor nulo
        self._refs = None
        self._ano = None
        self._mes = None
        self._mask = ''

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

        nivel_filter = 'AND r.NIVEL_ESTRUTURA = {}'.format(self.nivel)

        rownum_filter = ''
        if rownum is not None:
            rownum_filter = 'WHERE rownum <= {}'.format(rownum)

        sql = """
            WITH SEL AS
            (
            SELECT
              r.NIVEL_ESTRUTURA NIVEL
            , r.REFERENCIA REF
            FROM BASI_030 r
            WHERE r.REFERENCIA NOT LIKE 'DV%'
              {nivel_filter} -- nivel_filter
              AND r.REFERENCIA = 'CA010'
            ORDER BY
              r.REFERENCIA
            )
            SELECT
              s.*
            FROM SEL s
            {rownum_filter} -- rownum_filter
        """.format(
            nivel_filter=nivel_filter,
            rownum_filter=rownum_filter,
        )
        # print(sql)
        self._refs = self._ora.execute(sql)

    def param_ok(self):
        if self.ano is None or \
                self.mes is None or \
                self._refs is None:
            raise ValueError(
                "Refs, ano e mes pós inventário devem ser informados")

    def print_inventario(self):
        self.param_ok()
        self._print_fields = True
        count = len(self._refs['data'])
        for i, values in enumerate(self._refs['data']):
            row = dict(zip(self._refs['keys'], values))
            sys.stderr.write(
                '({}/{}) {}.{}\n'.format(i+1, count, row['NIVEL'], row['REF']))
            self.print_ref_inv(row['NIVEL'], row['REF'])

    def print_ref_inv(self, nivel, ref):
        fitro_nivel = "AND e.NIVEL_ESTRUTURA = {}".format(nivel)

        fitro_ref = "AND e.GRUPO_ESTRUTURA = '{}'".format(ref)

        fitro_data = '''--
            AND e.DATA_MOVIMENTO < TO_DATE('{ano}-{mes}-01','YYYY-MM-DD')
        '''.format(ano=self.ano, mes=self.mes)

        sql = """
            SELECT
              e.NIVEL_ESTRUTURA NIVEL
            , e.GRUPO_ESTRUTURA REF
            , r.DESCR_REFERENCIA REF_DESCR
            , r.UNIDADE_MEDIDA REF_UNID
            , um.UNID_MED_TRIB UNIDADE
            , e.SUBGRUPO_ESTRUTURA TAM
            , t.DESCR_TAM_REFER TAM_DESCR
            , e.ITEM_ESTRUTURA COR
            , i.DESCRICAO_15 COR_DESCR
            , i.PRECO_CUSTO_INFO PRECO_INFORMADO
            , sum(e.saldo_fisico) QTD
            , sum(e.saldo_financeiro)
              / sum(e.saldo_fisico) PRECO
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
                WHERE 1=1
                  {fitro_nivel} -- fitro_nivel
                  {fitro_ref} -- fitro_ref
                  -- AND e.DATA_MOVIMENTO < TO_DATE('2019-01-01','YYYY-MM-DD')
                  {fitro_data} -- fitro_data
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
            JOIN basi_030 r
              ON r.NIVEL_ESTRUTURA = e.NIVEL_ESTRUTURA
             AND r.REFERENCIA = e.GRUPO_ESTRUTURA
             AND r.DESCR_REFERENCIA NOT LIKE '-%'
            JOIN basi_200 um
              ON um.unidade_medida = r.UNIDADE_MEDIDA
            JOIN basi_020 t
              ON t.BASI030_NIVEL030 = e.NIVEL_ESTRUTURA
             AND t.BASI030_REFERENC = e.GRUPO_ESTRUTURA
             AND t.TAMANHO_REF = e.SUBGRUPO_ESTRUTURA
             AND t.DESCR_TAM_REFER NOT LIKE '-%'
            JOIN basi_010 i
              ON i.NIVEL_ESTRUTURA = e.NIVEL_ESTRUTURA
             AND i.GRUPO_ESTRUTURA = e.GRUPO_ESTRUTURA
             AND i.SUBGRU_ESTRUTURA = e.SUBGRUPO_ESTRUTURA
             AND i.ITEM_ESTRUTURA = e.ITEM_ESTRUTURA
             AND i.DESCRICAO_15 NOT LIKE '-%'
            WHERE 1=1
              AND e.saldo_fisico >= 1
              AND e.saldo_financeiro > 0
            GROUP BY
              e.NIVEL_ESTRUTURA
            , e.GRUPO_ESTRUTURA
            , r.DESCR_REFERENCIA
            , r.UNIDADE_MEDIDA
            , um.UNID_MED_TRIB
            , e.SUBGRUPO_ESTRUTURA
            , t.DESCR_TAM_REFER
            , e.ITEM_ESTRUTURA
            , i.DESCRICAO_15
            , i.PRECO_CUSTO_INFO
            ORDER BY
              e.NIVEL_ESTRUTURA
            , e.GRUPO_ESTRUTURA
            , e.SUBGRUPO_ESTRUTURA
            , e.ITEM_ESTRUTURA
        """.format(
            fitro_nivel=fitro_nivel,
            fitro_ref=fitro_ref,
            fitro_data=fitro_data,
        )
        # print(sql)
        ref_invent = self._ora.execute(sql)

        for values in ref_invent['data']:
            row = dict(zip(ref_invent['keys'], values))
            row['QTD'] = round(row['QTD'], 2)
            # Se preço baseado no saldo_financeiro for muito diferente do
            # informado, usa o atualmente informado
            if row['PRECO'] > row['PRECO_INFORMADO']*1.2 or \
                    row['PRECO'] < row['PRECO_INFORMADO']*0.8:
                row['PRECO'] = round(row['PRECO_INFORMADO'], 4)
            else:
                row['PRECO'] = round(row['PRECO'], 4)
            row['VALOR'] = row['QTD'] * row['PRECO']
            row['CODIGO'] = '{}.{}.{}.{}'.format(
                row['NIVEL'],
                row['REF'],
                row['TAM'],
                row['COR'],
            )
            row['DESCRICAO'] = '{} {} {} {}'.format(
                row['CODIGO'],
                row['REF_DESCR'],
                row['TAM_DESCR'],
                row['COR_DESCR'],
            )
            row['CONTA_CONTABIL'] = 377
            colunas = {
                'CODIGO': 'Código',
                'DESCRICAO': 'Descrição',
                'UNIDADE': 'Unidade',
                'QTD': 'Quantidade',
                'PRECO': 'Valor unitário',
                'VALOR': 'Valor total',
                'CONTA_CONTABIL': 'Conta contábil',
            }
            self.print_row(row, colunas)

    def print_row(self, row, colunas=None):
        if colunas is not None:
            row = {colunas[key]: row[key] for key in colunas.keys()}
        values = list(row.values())
        keys = row.keys()
        if self._print_fields:
            self._mask = self.make_csv_mask(values)
            print(';'.join(keys))
            self._print_fields = False
        for i in range(len(values)):
            if not isinstance(values[i], str):
                values[i] = locale.currency(
                    values[i], grouping=True, symbol=None)
        print(self._mask.format(*values))

    def make_csv_mask(self, values):
        sep = ''
        result = ''
        for val in values:
            if isinstance(val, str):
                result += sep + '"{}"'
            else:
                result += sep + '{}'
            sep = ';'
        return result


def parse_args():
    parser = argparse.ArgumentParser(
        description='Gera CSV de inventário',
        epilog="(c) Tussor & Oxigenai",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "nivel",
        help='Nivel dos produtos (1, 2 ou 9)',
        type=int,
        choices=[1, 2, 9],
        )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    print(args.nivel)

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    ora = Oracle()
    ora.connect()

    inv = Inventario(ora)
    inv.nivel = args.nivel

    # inv.get_refs(nivel=9, rownum=10)
    inv.get_refs()

    inv.ano = '2019'
    inv.mes = '01'
    inv.print_inventario()

    ora.close()
