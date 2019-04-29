#!/usr/bin/env python

import sys
import cx_Oracle
import psycopg2
from pprint import pprint
import locale
import argparse
from datetime import datetime, timedelta

from db_password import DBPASS_POSTGRE, DBPASS_ORACLE


class Oracle:

    def __init__(self):
        self.username = 'systextil'
        self.password = DBPASS_ORACLE
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
            if self.con:
                if self.cursor is not None:
                    self.cursor.close()
                self.con.close()
        except cx_Oracle.DatabaseError as e:
            print('[Closing error] {}'.format(e))
            sys.exit(4)


class Postgre:

    def __init__(self):
        self.username = "tussor_fo2"
        self.password = DBPASS_POSTGRE
        self.hostname = "127.0.0.1"
        self.port = 25432
        self.database = "tussor_fo2_production"

    def connect(self):
        try:
            self.con = psycopg2.connect(
                user=self.username,
                password=self.password,
                host=self.hostname,
                port=self.port,
                database=self.database,
            )
        except psycopg2.Error as e:
            print('[Connection error] {}'.format(e))
            sys.exit(1)

        self.cursor = self.con.cursor()

        try:
            self.cursor.execute(
                'SELECT version();')
        except psycopg2.Error as e:
            print('[Cursor test error] {}'.format(e))
            sys.exit(2)

    def execute(self, sql, **xargs):
        try:
            if len(xargs.keys()) == 0:
                self.cursor.execute(sql)
            else:
                self.cursor.execute(sql, xargs)
        except psycopg2.Error as e:
            print('[Execute error] {}'.format(e))
            sys.exit(3)

        result = {
            'keys': [f[0] for f in self.cursor.description],
            'data': self.cursor.fetchall(),
        }
        return result

    def close(self):
        try:
            if self.con:
                if self.cursor is not None:
                    self.cursor.close()
                self.con.close()
        except psycopg2.Error as e:
            print('[Closing error] {}'.format(e))
            sys.exit(4)


class Inventario:

    def __init__(self, db):
        # inicializado via parâmetros
        self._db = db

        # inicialização fixa
        self._print_header = True

        # parametros - valor default (ou None)
        self._tipo = None
        self._nivel = None
        self._ref = None
        self._ano = None
        self._mes = None
        self._prolong = None

        # outras variaveis utilizadas
        self._refs = None
        self._mask = ''
        self._colunas = None
        self._tipo_params = None

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, value):
        self._tipo = value

    @property
    def nivel(self):
        return self._nivel

    @nivel.setter
    def nivel(self, value):
        self._nivel = value

    @property
    def ref(self):
        return self._ref

    @ref.setter
    def ref(self, value):
        self._ref = value

    @property
    def prolong(self):
        return self._prolong

    @prolong.setter
    def prolong(self, value):
        self._prolong = value
        if value:
            self._print_header = False

    @property
    def ano(self):
        return self._ano

    @ano.setter
    def ano(self, value):
        if isinstance(value, int):
            self._ano = '{}'.format(value)
        else:
            self._ano = value

    @property
    def mes(self):
        return self._mes

    @mes.setter
    def mes(self, value):
        if isinstance(value, int):
            self._mes = '{:02}'.format(value)
        else:
            self._mes = value

    def get_refs(self, nivel=None, rownum=None):
        if nivel is None:
            nivel = self.nivel
        else:
            self.nivel = nivel

        nivel_filter = "AND r.NIVEL_ESTRUTURA = {}".format(self.nivel)

        insumos_de_alternativa = ''
        if nivel != 1:
            insumos_de_alternativa = '''--
                JOIN BASI_050 ia -- insumos de alternativa
                  ON ia.NIVEL_COMP = r.NIVEL_ESTRUTURA
                 AND ia.GRUPO_COMP = r.REFERENCIA
            '''
        ref_filter = ""
        if self.ref is not None:
            ref_filter = "AND r.REFERENCIA = '{}'".format(self.ref)
        else:
            if nivel == 1:
                ref_filter = "AND r.REFERENCIA <= '99999'"

        rownum_filter = ''
        if rownum is not None:
            rownum_filter = 'WHERE rownum <= {}'.format(rownum)

        sql = """
            WITH SEL AS
            (
            SELECT DISTINCT
              r.NIVEL_ESTRUTURA NIVEL
            , r.REFERENCIA REF
            FROM BASI_030 r
            {insumos_de_alternativa} -- insumos_de_alternativa
            WHERE r.REFERENCIA NOT LIKE 'DV%'
              {nivel_filter} -- nivel_filter
              {ref_filter} -- ref_filter
            ORDER BY
              r.REFERENCIA
            )
            SELECT
              s.*
            FROM SEL s
            {rownum_filter} -- rownum_filter
        """.format(
            insumos_de_alternativa=insumos_de_alternativa,
            nivel_filter=nivel_filter,
            ref_filter=ref_filter,
            rownum_filter=rownum_filter,
        )
        # print(sql)
        self._refs = self._db.execute(sql)

    def param_ok(self):
        if self.ano is None or \
                self.mes is None or \
                self._refs is None:
            raise ValueError(
                "Refs, ano e mes pós inventário devem ser informados")

    def print(self):
        self.param_ok()
        count = len(self._refs['data'])
        for i, values in enumerate(self._refs['data']):
            row = dict(zip(self._refs['keys'], values))
            sys.stderr.write(
                '({}/{}) {}.{}\n'.format(i+1, count, row['NIVEL'], row['REF']))
            self.print_ref(row['NIVEL'], row['REF'])

    def print_ref(self, nivel, ref):
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
                JOIN BASI_030 r
                  ON r.NIVEL_ESTRUTURA = e.NIVEL_ESTRUTURA
                 AND r.REFERENCIA = e.GRUPO_ESTRUTURA
                WHERE 1=1
                  {fitro_nivel} -- fitro_nivel
                  {fitro_ref} -- fitro_ref
                  -- AND e.DATA_MOVIMENTO < TO_DATE('2019-01-01','YYYY-MM-DD')
                  {fitro_data} -- fitro_data
                  AND 1 = (
                    CASE WHEN e.NIVEL_ESTRUTURA = 2 THEN
                      CASE WHEN e.CODIGO_DEPOSITO = 202 THEN 1 ELSE 0 END
                    WHEN e.NIVEL_ESTRUTURA = 9 THEN
                      CASE WHEN r.CONTA_ESTOQUE = 22 THEN
                        CASE WHEN e.CODIGO_DEPOSITO = 212 THEN 1 ELSE 0 END
                      ELSE
                        CASE WHEN e.CODIGO_DEPOSITO = 231 THEN 1 ELSE 0 END
                      END
                    ELSE -- i.NIVEL_ESTRUTURA = 1
                      CASE WHEN e.CODIGO_DEPOSITO in (101, 102) THEN 1
                      ELSE 0 END
                    END
                  )
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
        ref_invent = self._db.execute(sql)

        if self.tipo == 'i':
            self._tipo_params = {
                'colunas': {
                    'CODIGO': 'Código',
                    'DESCRICAO': 'Descrição',
                    'UNIDADE': 'Unidade',
                    'QTD': 'Quantidade',
                    'PRECO': 'Valor unitário',
                    'VALOR': 'Valor total',
                    'CONTA_CONTABIL': 'Conta contábil',
                }
            }
        else:
            dt_pos_fim = datetime.strptime(
                '01/{mes}/{ano}'.format(mes=self.mes, ano=self.ano),
                '%d/%m/%Y')
            dt_fim = dt_pos_fim-timedelta(days=1)
            dt_fim_str = dt_fim.strftime('%d%m%Y')
            dt_ini = dt_fim-timedelta(days=dt_fim.day-1)
            dt_ini_str = dt_ini.strftime('%d%m%Y')
            self._tipo_params = {
                'colunas': [
                    'REG',
                    'COD_ITEM',
                    'DT_EST',
                    'QTD',
                    'IND_EST',
                    'COD_PART',
                ],
                'DT_INI': dt_ini_str,
                'DT_FIN': dt_fim_str,
            }

        for values in ref_invent['data']:
            row = dict(zip(ref_invent['keys'], values))
            if self.tipo == 'i':
                self.print_ref_inv(row)
            else:
                self.print_ref_blocok(row)

    def print_ref_inv(self, row):
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
        self.print_csv_row(row)

    def print_ref_blocok(self, row):
        row['REG'] = 'K200'
        row['COD_ITEM'] = '{}.{}.{}.{}'.format(
            row['NIVEL'],
            row['REF'],
            row['TAM'],
            row['COR'],
        )
        row['DT_EST'] = self._tipo_params['DT_FIN']
        row['QTD'] = round(row['QTD'], 3)
        row['IND_EST'] = '0'
        row['COD_PART'] = ''
        self.print_pipe_row(row)

    def print_csv_row(self, row):
        if 'colunas' in self._tipo_params:
            cols = self._tipo_params['colunas']
            row = {cols[key]: row[key] for key in cols.keys()}
        values = list(row.values())
        keys = row.keys()
        if self._print_header:
            self._mask = self.make_csv_mask(values)
            print(';'.join(keys))
            self._print_header = False
        for i in range(len(values)):
            if not isinstance(values[i], str):
                values[i] = locale.currency(
                    values[i], grouping=True, symbol=None)
        print(self._mask.format(*values))

    def print_pipe_row(self, row):
        if 'colunas' in self._tipo_params:
            cols = self._tipo_params['colunas']
            row = {key: row[key] for key in cols}
        values = list(row.values())
        if self._print_header:
            print('|K001|0|')
            print('|K100|{}|{}|'.format(
                self._tipo_params['DT_INI'],
                self._tipo_params['DT_FIN'],
            ))
            self._print_header = False
        self._mask = self.make_pipe_mask(values)
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

    def make_pipe_mask(self, values):
        result = '|'
        for _ in range(len(values)):
            result += '{}|'
        return result


def parse_args():
    parser = argparse.ArgumentParser(
        description='Gera CSV de inventário',
        epilog="(c) Tussor & Oxigenai",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "origem",
        choices=['s', 'f'],
        help='Origem dos dados (Systextil ou Fo2-intranet)')
    parser.add_argument(
        "-p", "--prolong",
        help='Não imprime header',
        action='store_true')
    parser.add_argument(
        "tipo",
        help='Tipo de saída (Inventário ou blocoK)',
        choices=['i', 'k'],
        )
    parser.add_argument(
        "ano",
        help='Ano do mês pós inventário',
        type=int,
        metavar="{2019-2029}",
        choices=range(2019, 2030),
        )
    parser.add_argument(
        "mes",
        help='Mês pós inventário',
        type=int,
        metavar="{1-12}",
        choices=range(1, 13),
        )
    parser.add_argument(
        "nivel",
        help='Nivel dos produtos (1, 2 ou 9)',
        type=int,
        choices=[1, 2, 9],
        )
    parser.add_argument(
        "rownum",
        help='Limite na quantidade de produtos',
        type=int,
        nargs='?',
        )
    parser.add_argument(
        "-r", "--ref",
        type=str,
        help='Força apenas esse referência')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    db = Oracle()
    db.connect()

    inv = Inventario(db)
    inv.tipo = args.tipo
    inv.nivel = args.nivel
    inv.ref = args.ref
    inv.prolong = args.prolong

    inv.get_refs(rownum=args.rownum)

    inv.ano = args.ano
    inv.mes = args.mes
    inv.print()

    db.close()
