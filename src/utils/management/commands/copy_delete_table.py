import sys
import datetime
from pprint import pprint, pformat

from django.core.management.base import BaseCommand, CommandError

from fo2.connections import db_cursor, db_cursor_so

import base.models
from utils.functions.models.dictlist import dictlist_lower

import lotes.models as models


class Command(BaseCommand):
    help = 'Move tabela do banco do systextil para o banco da intranet'

    def add_arguments(self, parser):
        parser.add_argument(
            'tabela',
            help='Indica uma tabela específica a ser movida')

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def my_pprintln(self, object):
        self.my_pprint(object, ending='\n')

    def my_pprint(self, object, ending=''):
        self.stdout.write(pformat(object), ending=ending)
        self.stdout.flush()

    def iter_cursor(self, cursor):
        columns = [i[0].lower() for i in cursor.description]
        for row in cursor:
            dict_row = dict(zip(columns, row))
            yield dict_row

    def data_cursor(self, iter):
        data = []
        for row in iter:
            data.append(row)
        return data

    def get_last_table_data(self):
        cursor_s = db_cursor_so()
        sql = '''
            SELECT
              hh.*
            FROM
            ( SELECT
                h.DATA_OCORR
              FROM table h
              ORDER BY
                h.DATA_OCORR DESC
            ) hh
            WHERE rownum = 1
        '''
        data_s = list(cursor_s.execute(sql))
        if len(data_s) == 0:
            return None
        else:
            return data_s[0][0]

    def get_table(self, data):
        cursor_s = db_cursor_so()
        sql = '''
            SELECT
              h.*
            FROM table h
            WHERE h.DATA_OCORR < %s
        '''
        cursor_s.execute(sql, [data])
        return self.iter_cursor(cursor_s)

    def insert_table(self, row):
        cursor_f = db_cursor('default')
        sql = f'''
            INSERT INTO systextil_logs.table
            ( tabela
            , sequencia
            , operacao
            , data_ocorr
            , usuario
            , usuario_rede
            , maquina_rede
            , num01
            , num02
            , num03
            , num04
            , num05
            , num06
            , num07
            , num08
            , num09
            , num10
            , dat01
            , dat02
            , dat03
            , dat04
            , dat05
            , dat06
            , dat07
            , str01
            , str02
            , str03
            , str04
            , str05
            , str06
            , str07
            , str08
            , str09
            , str10
            , long01
            , aplicacao
            , programa
            , lote
            )
            VALUES
            ( '{row["tabela"]}'
            , {row["sequencia"]}
            , '{row["operacao"]}'
            , {row["data_ocorr"]}
            , '{row["usuario"]}'
            , '{row["usuario_rede"]}'
            , '{row["maquina_rede"]}'
            , {row["num01"]}
            , {row["num02"]}
            , {row["num03"]}
            , {row["num04"]}
            , {row["num05"]}
            , {row["num06"]}
            , {row["num07"]}
            , {row["num08"]}
            , {row["num09"]}
            , {row["num10"]}
            , {row["dat01"]}
            , {row["dat02"]}
            , {row["dat03"]}
            , {row["dat04"]}
            , {row["dat05"]}
            , {row["dat06"]}
            , {row["dat07"]}
            , '{row["str01"]}'
            , '{row["str02"]}'
            , '{row["str03"]}'
            , '{row["str04"]}'
            , '{row["str05"]}'
            , '{row["str06"]}'
            , '{row["str07"]}'
            , '{row["str08"]}'
            , '{row["str09"]}'
            , '{row["str10"]}'
            , '{row["long01"]}'
            , '{row["aplicacao"]}'
            , '{row["programa"]}'
            , {row["lote"]}
            )
        '''
        cursor_f.execute(sql)

    def none_0(self, valor):
        return 0 if valor is None else valor

    def quote_str(self, valor):
        return "''".join(valor.split("'"))

    def none_str_empty(self, valor):
        return '' if valor is None else self.quote_str(valor)

    def none_null(self, valor):
        return 'NULL' if valor is None else f"'{valor}'"

    def n_none_0(self, row, campos):
        for campo in campos:
            row[campo] = self.none_0(row[campo])

    def n_none_str_empty(self, row, campos):
        for campo in campos:
            row[campo] = self.none_str_empty(row[campo])

    def n_none_null(self, row, campos):
        for campo in campos:
            row[campo] = self.none_null(row[campo])

    def trata_none(self, row):
        self.n_none_0(
            row,
            [
                'sequencia',
                'num01',
                'num02',
                'num03',
                'num04',
                'num05',
                'num06',
                'num07',
                'num08',
                'num09',
                'num10',
                'lote',
            ]
        )
        self.n_none_str_empty(
            row,
            [
                'tabela',
                'operacao',
                'usuario',
                'usuario_rede',
                'maquina_rede',
                'str01',
                'str02',
                'str03',
                'str04',
                'str05',
                'str06',
                'str07',
                'str08',
                'str09',
                'str10',
                'long01',
                'aplicacao',
                'programa',
            ]
        )
        self.n_none_null(
            row,
            [
                'data_ocorr',
                'dat01',
                'dat02',
                'dat03',
                'dat04',
                'dat05',
                'dat06',
                'dat07',
            ]
        )

    def del_table(self, data):
        cursor_s = db_cursor_so()
        sql = '''
            DELETE FROM table h
            WHERE h.DATA_OCORR < %s
        '''
        cursor_s.execute(sql, [data])

    def existe_s_table(self, cursor, owner, name):
        try:
            sql = f'''
                SELECT
                  upper(t.TABLE_NAME)
                FROM ALL_TABLES t
                WHERE 1=1
                  AND upper(t.OWNER) = '{owner.upper()}'
                  AND upper(t.TABLE_NAME) = '{name.upper()}'
            '''
            data = list(cursor.execute(sql))
            return data[0][0] == name.upper()
        except Exception as e:
            return False

    def existe_l_table(self, cursor, name):
        try:
            sql = f'''
                SELECT
                  name
                FROM sqlite_master
                WHERE type='table'
                  AND upper(name) = upper('{name.upper()}')
            '''
            data = list(cursor.execute(sql))
            return data[0][0] == name.upper()
        except Exception as e:
            return False

    def existe_f_table(self, cursor, schema, name):
        try:
            sql = f'''
                SELECT EXISTS (
                  select table_name
                  FROM information_schema.tables
                  WHERE 1=1
                    AND upper(table_schema = upper('{schema}')
                    AND upper(table_name)   = upper('{name}')
                )
            '''
            data = list(cursor.execute(sql))
            return data[0][0]
        except Exception as e:
            return False

    def verifica_s_tabela(self, tabela):
        cursor = db_cursor_so()
        existe = self.existe_s_table(cursor, 'SYSTEXTIL', tabela)
        if existe:
            self.my_println('systextil tem tabela')
        else:
            self.my_println('systextil não tem tabela')
        return existe

    def verifica_l_tabela(self, tabela):
        cursor = db_cursor('default')
        existe = self.existe_l_table(cursor, tabela)
        if existe:
            self.my_println('sqlite tem tabela')
        else:
            self.my_println('sqlite não tem tabela')
        return existe

    def verifica_f_tabela(self, tabela):
        cursor = db_cursor('default')
        existe = self.existe_f_table(cursor, 'systextil_logs', tabela)
        if existe:
            self.my_println('postgre tem tabela')
        else:
            self.my_println('postgre não tem tabela')
        return existe

    def verificacoes(self):
        return self.verifica_s_tabela(self.tabela) \
            and self.verifica_l_tabela(self.tabela)

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        self.tabela = options['tabela']

        try:

            if not self.verificacoes():
                raise CommandError(
                    f'Tabela "{self.tabela}" não encontrada')

            raise SystemExit(1)

            data = self.get_last_table_data()
            self.my_println(f"data {data}")

            ics = self.get_table(data)

            count = 0
            for row in ics:
                count += 1
                self.trata_none(row)
                self.my_print(".")
                self.insert_table(row)
            self.my_println(f"{count} registros copiados")

            self.del_table(data)

        except Exception as e:
            raise CommandError('Erro movendo table "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
