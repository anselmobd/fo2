import sys
import datetime
from pprint import pprint, pformat

from django.core.management.base import BaseCommand, CommandError

from fo2.connections import db_cursor, db_cursor_so

import base.models
from utils.functions.models import rows_to_dict_list_lower

import lotes.models as models


class Command(BaseCommand):
    help = 'Move HIST_100 do banco do systextil para o banco da intranet'
    __MAX_TASKS = 10000000

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

    def get_last_hist_100_data_dias(self, dias):
        cursor_s = db_cursor_so()

        if dias > 1:
            self.my_println(f'N dias: {dias}')

        as_of = "as of timestamp timestamp '2021-08-24 16:22:25'"

        sql = f'''
            WITH pridata AS
            (
              SELECT
                min(hp.DATA_OCORR) DATA_OCORR
              FROM systextil.HIST_100 {as_of} hp
            )
            , dias AS 
            (
              SELECT 
                max(hd.DATA_OCORR) DATA_OCORR 
              FROM pridata p
              JOIN systextil.HIST_100 {as_of} hd
                ON hd.DATA_OCORR < p.DATA_OCORR + {dias}
            )
            SELECT 
              max(d.DATA_OCORR) 
            FROM dias d
            JOIN pridata p
              ON d.DATA_OCORR <> p.DATA_OCORR
        '''
        data_s = list(cursor_s.execute(sql))

        if len(data_s) == 0:
            return None
        return data_s[0][0]

    def get_last_hist_100_data(self):
        for d in range(1000,1030):
            data = self.get_last_hist_100_data_dias(d)
            if data:
                return data
        return None

    def get_hist_100(self, data):
        cursor_s = db_cursor_so()
        sql = '''
            SELECT
              h.*
            FROM HIST_100 h
            WHERE h.DATA_OCORR < %s
        '''
        cursor_s.execute(sql, [data])
        return self.iter_cursor(cursor_s)

    def insert_hist_100(self, row):
        cursor_f = db_cursor('default')
        sql = f'''
            INSERT INTO systextil_logs.hist_100
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

    def del_hist_100(self, data):
        cursor_s = db_cursor_so()
        sql = '''
            DELETE FROM HIST_100 h
            WHERE h.DATA_OCORR < %s
        '''
        cursor_s.execute(sql, [data])

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        try:
            data = self.get_last_hist_100_data()
            self.my_println(f"data {data}")

            ics = self.get_hist_100(data)

            count = 0
            ult_data_ocorr = None
            can_break = False
            for row in ics:
                count += 1
                if (ult_data_ocorr is None or
                        ult_data_ocorr != row['data_ocorr']):
                    if can_break:
                        break
                    ult_data_ocorr = row['data_ocorr']

                self.trata_none(row)
                self.my_print(".")
                self.insert_hist_100(row)

                if count >= self.__MAX_TASKS:
                    can_break = True

            self.my_println(f"{count} registros copiados")

            if ult_data_ocorr is not None:
                self.my_println(f"ultima data transferida: {ult_data_ocorr}")
                self.del_hist_100(ult_data_ocorr)

        except Exception as e:
            raise CommandError('Erro movendo HIST_100 "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
