import sys
import datetime
from pprint import pprint, pformat

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, connections

import base.models
from utils.functions.models import rows_to_dict_list_lower

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
        cursor_s = connections['so'].cursor()
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
        cursor_s = connections['so'].cursor()
        sql = '''
            SELECT
              h.*
            FROM table h
            WHERE h.DATA_OCORR < %s
        '''
        cursor_s.execute(sql, [data])
        return self.iter_cursor(cursor_s)

    def insert_table(self, row):
        cursor_f = connections['default'].cursor()
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
        cursor_s = connections['so'].cursor()
        sql = '''
            DELETE FROM table h
            WHERE h.DATA_OCORR < %s
        '''
        cursor_s.execute(sql, [data])

    def existe_table(self, cursor, owner, name):
        try:
            sql = f'''
                SELECT
                  t.TABLE_NAME
                FROM ALL_TABLES t
                WHERE 1=1
                  AND t.OWNER = '{owner}'
                  AND t.TABLE_NAME = '{name}'
            '''
            data = list(cursor.execute(sql))
            return data[0][0] == name
        except Exception as e:
            return False

    def verifica_s_tabela(self, tabela):
        cursor_vs = connections['so'].cursor()
        return self.existe_table(cursor_vs, 'SYSTEXTIL', tabela)

    def verificacoes(self):
        return self.verifica_s_tabela(self.tabela)

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        self.tabela = options['tabela']

        try:

            if self.verificacoes():
                self.my_println('tem tabela')
                raise SystemExit(1)
            else:
                self.my_println('não tem tabela')
                raise CommandError(
                    f'Tabela "{self.tabela}" não encontrada no systextil')

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
