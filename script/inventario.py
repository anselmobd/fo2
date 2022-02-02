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

    def __init__(self,
        username='systextil',
        password=DBPASS_ORACLE,
        hostname='localhost',
        port=28521,
        servicename='XE',
        schema='SYSTEXTIL',
    ):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.port = port
        self.servicename = servicename
        self.schema = schema

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
        self._origem = None
        self._tipo = None
        self._nivel = None
        self._ref = None
        self._rownum = None
        self._ano = None
        self._mes = None
        self._prolong = None

        # outras variaveis utilizadas
        self._refs = None
        self._mask = ''
        self._colunas = None
        self._tipo_params = None

    @property
    def origem(self):
        return self._origem

    @origem.setter
    def origem(self, value):
        self._origem = value

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
    def rownum(self):
        return self._rownum

    @rownum.setter
    def rownum(self, value):
        self._rownum = value

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

    def get_refs(self):
        if self.origem == 's':
            sql = self.get_sql_systextil_refs()
        else:
            sql = self.get_sql_fo2_refs()
        self._refs = self._db.execute(sql)

    def get_sql_systextil_refs(self):
        nivel_filter = "AND r.NIVEL_ESTRUTURA = {}".format(self.nivel)

        insumos_de_alternativa = ''
        if self.nivel != 1:
            insumos_de_alternativa = '''--
                JOIN BASI_050 ia -- insumos de alternativa
                  ON ia.NIVEL_COMP = r.NIVEL_ESTRUTURA
                 AND ia.GRUPO_COMP = r.REFERENCIA
            '''
        ref_filter = ""
        if self.ref is not None:
            ref_filter = "AND r.REFERENCIA = '{}'".format(self.ref)
        else:
            if self.nivel == 1:
                ref_filter = "AND r.REFERENCIA <= '99999'"

        rownum_filter = ''
        if self.rownum is not None:
            rownum_filter = 'WHERE rownum <= {}'.format(self.rownum)

        sql = """
            WITH SEL AS
            (
            SELECT DISTINCT
              r.NIVEL_ESTRUTURA NIVEL
            , r.REFERENCIA REF
            FROM BASI_030 r
            {insumos_de_alternativa} -- insumos_de_alternativa
            WHERE r.REFERENCIA NOT LIKE 'DV%' -- diversos
              AND (r.NIVEL_ESTRUTURA != 9
                   OR r.REFERENCIA != 'IP001') -- inspecao
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
        return sql

    def get_sql_fo2_refs(self):
        nivel_filter = ""
        if self.nivel != 1:
            nivel_filter = "AND 1=2"

        ref_filter = ""
        if self.ref is not None:
            ref_filter = "AND e.referencia = '{}'".format(self.ref)
        else:
            if self.nivel == 1:
                ref_filter = "AND e.referencia <= '99999'"

        fitro_data = '''--
            AND e."data" < TO_DATE('{ano}-{mes}-01','YYYY-MM-DD')
        '''.format(ano=self.ano, mes=self.mes)

        rownum_filter = ''
        if self.rownum is not None:
            rownum_filter = 'limit {}'.format(self.rownum)

        sql = f"""
            select distinct
              '1' "NIVEL"
            , e.referencia "REF"
            from fo2_estoque_manual e
            JOIN (
              SELECT
                max(e."data") DATA_BUSCA
              FROM fo2_estoque_manual e
              WHERE 1=1
                {fitro_data} -- fitro_data
            ) edata
              on edata.data_busca = e."data"
            where 1=1
              {nivel_filter} -- nivel_filter
              {ref_filter} -- ref_filter
            order by
              e.referencia
            {rownum_filter} -- rownum_filter
        """
        return sql

    def print(self):
        self.get_refs()
        count = len(self._refs['data'])
        for i, values in enumerate(self._refs['data']):
            row = dict(zip(self._refs['keys'], values))
            sys.stdout.flush()
            sys.stderr.write(
                '({}/{}) {}.{}\n'.format(i+1, count, row['NIVEL'], row['REF']))
            self.print_ref(row['NIVEL'], row['REF'])

    def get_quant_sql(self, nivel, ref):
        if self.origem == 's':
            sql = self.get_quant_systextil_sql(nivel, ref)
        else:
            sql = self.get_quant_fo2_sql(nivel, ref)
        return sql

    def get_quant_fo2_sql(self, nivel, ref):
        fitro_nivel = ""
        if self.nivel != 1:
            fitro_nivel = "AND 1=2"

        fitro_ref = "AND e.referencia = '{}'".format(ref)

        fitro_data = '''--
            AND e."data" < TO_DATE('{ano}-{mes}-01','YYYY-MM-DD')
        '''.format(ano=self.ano, mes=self.mes)

        sql = """
            SELECT
              '1' "NIVEL"
            , e.referencia "REF"
            , p.descricao "REF_DESCR"
            , p.unidade "REF_UNID"
            , p.unidade "UNIDADE"
            , '04' "TIPO_ITEM"
            , p.ncm "NCM"
            , 18 "ALIQ_ICMS"
            , e.tamanho "TAM"
            , pt.descricao "TAM_DESCR"
            , e.cor "COR"
            , pc.descricao "COR_DESCR"
            , i.custo "PRECO_INFORMADO"
            , e.qtd "QTD"
            , i.custo "PRECO"
            FROM fo2_estoque_manual e
            left join fo2_tamanho t
              on t.nome = e.tamanho
            JOIN (
              SELECT
                e.referencia
              , e.tamanho
              , e.cor
              , max(e."data") DATA_BUSCA
              FROM fo2_estoque_manual e
              WHERE 1=1
                {fitro_nivel} -- fitro_nivel
                {fitro_ref} -- fitro_ref
                {fitro_data} -- fitro_data
              GROUP BY
                e.referencia
              , e.tamanho
              , e.cor
            ) edt
              on edt.referencia = e.referencia
             and edt.tamanho    = e.tamanho
             and edt.cor        = e.cor
             and edt.data_busca = e."data"
            left join fo2_produto p
              on p.referencia = e.referencia
            left join fo2_produto_tamanho pt
              on pt.produto_id = p.id
             and pt.tamanho_id = t.id
            left join fo2_produto_cor pc
              on pc.produto_id = p.id
             and pc.cor = e.cor
            left join fo2_produto_item i
              on i.produto_id = p.id
             and i.tamanho_id = pt.id
             and i.cor_id = pc.id
            ORDER BY
              e.referencia
            , e.tamanho
            , e.cor
        """.format(
            fitro_nivel=fitro_nivel,
            fitro_ref=fitro_ref,
            fitro_data=fitro_data,
        )
        return sql

    def get_quant_systextil_sql(self, nivel, ref):
        fitro_nivel = "AND i.NIVEL_ESTRUTURA = {}".format(nivel)

        fitro_ref = "AND i.GRUPO_ESTRUTURA = '{}'".format(ref)

        fitro_data = '''--
            AND tr.DATA_MOVIMENTO < TO_DATE('{ano}-{mes}-01','YYYY-MM-DD')
        '''.format(ano=self.ano, mes=self.mes)

        sql = f"""
            SELECT
              s.NIVEL
            , s.REF
            , r.DESCR_REFERENCIA REF_DESCR
            , r.UNIDADE_MEDIDA REF_UNID
            , um.UNID_MED_TRIB UNIDADE
            , '01' TIPO_ITEM
            , r.CLASSIFIC_FISCAL NCM
            , 0 ALIQ_ICMS
            , s.TAM
            , t.DESCR_TAM_REFER TAM_DESCR
            , s.COR
            , i.DESCRICAO_15 COR_DESCR
            , i.PRECO_CUSTO_INFO PRECO_INFORMADO
            --, s.DATA_BUSCA
            --, e.saldo_financeiro
            --, e.saldo_fisico
            , CASE WHEN s.DATA_BUSCA IS NULL
              THEN s.QTD_STQ
              ELSE e.saldo_fisico
              END QTD
            , CASE WHEN s.DATA_BUSCA IS NULL
                     OR e.saldo_financeiro = 0
              THEN i.PRECO_CUSTO_INFO
              ELSE
                e.saldo_financeiro
                / e.saldo_fisico
              END PRECO
            FROM (
              SELECT
                r.NIVEL
              , r.REF
              , r.TAM
              , r.COR
              , r.CONTA_STQ
              , r.DEP
              , r.QTD_STQ
              , r.DATA_BUSCA
              , CASE WHEN r.DATA_BUSCA IS NULL
                THEN NULL
                ELSE
                ( SELECT
                    max(tr.SEQUENCIA_FICHA)
                  FROM ESTQ_300_ESTQ_310 tr
                  WHERE tr.NIVEL_ESTRUTURA = r.NIVEL
                    AND tr.GRUPO_ESTRUTURA = r.REF
                    AND tr.SUBGRUPO_ESTRUTURA = r.TAM
                    AND tr.ITEM_ESTRUTURA = r.COR
                    AND tr.DATA_MOVIMENTO = r.DATA_BUSCA
                )
                END SEQ_BUSCA
              FROM
              ( SELECT
                  i.NIVEL_ESTRUTURA NIVEL
                , i.GRUPO_ESTRUTURA REF
                , i.SUBGRU_ESTRUTURA TAM
                , i.ITEM_ESTRUTURA COR
                , r.CONTA_ESTOQUE CONTA_STQ
                , d.CODIGO_DEPOSITO DEP
                , e.QTDE_ESTOQUE_ATU QTD_STQ
                , ( SELECT
                      max(tr.DATA_MOVIMENTO)
                    FROM ESTQ_300_ESTQ_310 tr
                    WHERE tr.NIVEL_ESTRUTURA = i.NIVEL_ESTRUTURA
                      AND tr.GRUPO_ESTRUTURA = i.GRUPO_ESTRUTURA
                      AND tr.SUBGRUPO_ESTRUTURA = i.SUBGRU_ESTRUTURA
                      AND tr.ITEM_ESTRUTURA = i.ITEM_ESTRUTURA
                      -- AND tr.DATA_MOVIMENTO
                      --   < TO_DATE('2019-12-01','YYYY-MM-DD')
                      {fitro_data} -- fitro_data
                    ) DATA_BUSCA
                FROM BASI_010 i
                JOIN BASI_205 d ON 1=1
                JOIN BASI_030 r
                  ON r.NIVEL_ESTRUTURA = i.NIVEL_ESTRUTURA
                 AND r.REFERENCIA = i.GRUPO_ESTRUTURA
                JOIN ESTQ_040 e
                  ON e.CDITEM_NIVEL99 = i.NIVEL_ESTRUTURA
                 AND e.CDITEM_GRUPO = i.GRUPO_ESTRUTURA
                 AND e.CDITEM_SUBGRUPO = i.SUBGRU_ESTRUTURA
                 AND e.CDITEM_ITEM = i.ITEM_ESTRUTURA
                 AND e.LOTE_ACOMP = 0
                 AND e.DEPOSITO = d.CODIGO_DEPOSITO
                WHERE 1=1
                  -- AND i.NIVEL_ESTRUTURA = 9 -- fitro_nivel
                  {fitro_nivel} -- fitro_nivel
                  -- AND i.GRUPO_ESTRUTURA LIKE 'CA08%' -- fitro_ref
                  {fitro_ref} -- fitro_ref
                  -- AND e.DATA_MOVIMENTO < TO_DATE('2019-01-01','YYYY-MM-DD')
                  AND 1 = (
                    CASE WHEN i.NIVEL_ESTRUTURA = 2 THEN
                      CASE WHEN d.CODIGO_DEPOSITO = 202 THEN 1 ELSE 0 END
                    WHEN i.NIVEL_ESTRUTURA = 9 THEN
                      CASE WHEN r.CONTA_ESTOQUE = 22 THEN
                        CASE WHEN d.CODIGO_DEPOSITO = 212 THEN 1 ELSE 0 END
                      ELSE
                        CASE WHEN d.CODIGO_DEPOSITO = 231 THEN 1 ELSE 0 END
                      END
                    WHEN i.NIVEL_ESTRUTURA = 1 THEN
                      CASE WHEN d.CODIGO_DEPOSITO in (101, 102) THEN 1
                      ELSE 0 END
                    ELSE -- i.NIVEL_ESTRUTURA errado
                      0
                    END
                  )
                ORDER BY
                  i.NIVEL_ESTRUTURA
                , i.GRUPO_ESTRUTURA
                , i.SUBGRU_ESTRUTURA
                , i.ITEM_ESTRUTURA
                , d.CODIGO_DEPOSITO
              ) r
            ) s
            LEFT JOIN estq_310 e
              ON e.codigo_deposito    = s.dep
             and e.nivel_estrutura    = s.nivel
             and e.grupo_estrutura    = s.ref
             and e.subgrupo_estrutura = s.tam
             and e.item_estrutura     = s.cor
             and e.DATA_MOVIMENTO     = s.DATA_BUSCA
             and e.SEQUENCIA_FICHA    = s.SEQ_BUSCA
            JOIN basi_030 r
              ON r.NIVEL_ESTRUTURA = s.nivel
             AND r.REFERENCIA = s.ref
             AND r.DESCR_REFERENCIA NOT LIKE '-%'
            JOIN basi_200 um
              ON um.unidade_medida = r.UNIDADE_MEDIDA
            JOIN basi_020 t
              ON t.BASI030_NIVEL030 = s.nivel
             AND t.BASI030_REFERENC = s.ref
             AND t.TAMANHO_REF = s.tam
             AND t.DESCR_TAM_REFER NOT LIKE '-%'
            JOIN basi_010 i
              ON i.NIVEL_ESTRUTURA = s.nivel
             AND i.GRUPO_ESTRUTURA = s.ref
             AND i.SUBGRU_ESTRUTURA = s.tam
             AND i.ITEM_ESTRUTURA = s.cor
             AND i.DESCRICAO_15 NOT LIKE '-%'
            WHERE 1=1
              AND ( ( s.DATA_BUSCA IS NULL
                    AND s.QTD_STQ >= 1
                    )
                  OR
                    ( s.DATA_BUSCA IS NOT NULL
                    AND e.saldo_fisico >= 1
            --        AND e.saldo_financeiro > 0
                    )
                  )
            ORDER BY
              e.NIVEL_ESTRUTURA
            , e.GRUPO_ESTRUTURA
            , e.SUBGRUPO_ESTRUTURA
            , e.ITEM_ESTRUTURA
        """
        return sql

    def print_ref(self, nivel, ref):
        sql = self.get_quant_sql(nivel, ref)
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
        elif self.tipo == 'k':
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
                    'DT_EST',
                    'CODIGO',  # 'COD_ITEM'
                    'QTD',
                    'IND_EST',
                    'COD_PART',
                ],
                'DT_INI': dt_ini_str,
                'DT_FIN': dt_fim_str,
            }
        else:  # self.tipo == '2'
            self._tipo_params = {
                'colunas': [
                    'REG',
                    'CODIGO',  # 'COD_ITEM'
                    'DESCRICAO',  # 'DESCR_ITEM'
                    'COD_BARRA',
                    'COD_ANT_ITEM',
                    'UNIDADE',  # 'UNID_INV'
                    'TIPO_ITEM',
                    'NCM',  # 'COD_NCM'
                    'EX_IPI',
                    'COD_GEN',
                    'COD_LST',
                    'ALIQ_ICMS',
                    'CEST',
                ],
            }

        self._mask = None
        for values in ref_invent['data']:
            row = dict(zip(ref_invent['keys'], values))
            self.ref_calc(row)
            if self.tipo == 'i':
                self.print_ref_inv(row)
            elif self.tipo == 'k':
                self.print_ref_blocok(row)
            else:  # self.tipo == '2'
                self.print_ref_bloco0200(row)

    def ref_calc(self, row):
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

    def print_ref_inv(self, row):
        row['QTD'] = round(row['QTD'], 2)
        # Se preço baseado no saldo_financeiro for muito diferente do
        # informado, usa o atualmente informado
        if row['PRECO'] > float(row['PRECO_INFORMADO'])*1.2 or \
                row['PRECO'] < float(row['PRECO_INFORMADO'])*0.8:
            row['PRECO'] = round(row['PRECO_INFORMADO'], 4)
        else:
            row['PRECO'] = round(row['PRECO'], 4)
        row['VALOR'] = row['QTD'] * row['PRECO']
        row['CONTA_CONTABIL'] = 377
        self.print_csv_row(row)

    def print_ref_blocok(self, row):
        row['REG'] = 'K200'
        row['DT_EST'] = self._tipo_params['DT_FIN']
        row['QTD'] = round(row['QTD'], 3)
        row['IND_EST'] = '0'
        row['COD_PART'] = ''
        self.print_pipek_row(row)

    def print_ref_bloco0200(self, row):
        row['REG'] = '0200'
        row['COD_BARRA'] = ''
        row['COD_ANT_ITEM'] = ''
        row['EX_IPI'] = ''
        row['COD_GEN'] = row['NCM'][:2]
        row['COD_LST'] = ''
        row['CEST'] = ''
        self.print_pipe2_row(row)

    def print_csv_row(self, row):
        if 'colunas' in self._tipo_params:
            cols = self._tipo_params['colunas']
            row = {cols[key]: row[key] for key in cols.keys()}
        values = list(row.values())
        keys = row.keys()
        if self._print_header:
            print(';'.join(keys))
            self._print_header = False
        if self._mask is None:
            self._mask = self.make_csv_mask(values)
        self.print_row_values(values)

    def print_pipek_row(self, row):
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
        if self._mask is None:
            self._mask = self.make_pipe_mask(values)
        self.print_row_values(values)

    def print_pipe2_row(self, row):
        if 'colunas' in self._tipo_params:
            cols = self._tipo_params['colunas']
            row = {key: row[key] for key in cols}
        values = list(row.values())
        if self._mask is None:
            self._mask = self.make_pipe_mask(values)
        self.print_row_values(values)

    def print_row_values(self, values):
        for i in range(len(values)):
            if isinstance(values[i], str):
                values[i] = values[i].strip()
            else:
                values[i] = locale.currency(
                    values[i], grouping=False, symbol=None)
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
        help='Tipo de saída (Inventário, bloco K200 ou 0200)',
        choices=['i', 'k', '2'],
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

    if args.origem == 's':
        db = Oracle()
    else:
        db = Postgre()
    db.connect()

    inv = Inventario(db)
    inv.origem = args.origem
    inv.tipo = args.tipo
    inv.nivel = args.nivel
    inv.ref = args.ref
    inv.rownum = args.rownum
    inv.prolong = args.prolong
    inv.ano = args.ano
    inv.mes = args.mes
    inv.print()

    db.close()
