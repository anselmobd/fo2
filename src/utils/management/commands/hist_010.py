import sys
import datetime
from pprint import pprint, pformat

from django.core.management.base import BaseCommand, CommandError

from fo2.connections import db_cursor, db_cursor_so

import base.models
from utils.functions.models import rows_to_dict_list_lower

import lotes.models as models


class Command(BaseCommand):
    help = 'Move HIST_010 do banco do systextil para o banco da intranet'
    __MAX_TASKS = 10

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

    def get_last_hist_010_data(self):
        cursor_s = db_cursor_so()
        sql = '''
            SELECT
              hhh.*
            FROM
            ( SELECT
                hh.*
              FROM
              ( SELECT DISTINCT
                  h.DATA_OCORR
                FROM HIST_010 h
                ORDER BY
                  h.DATA_OCORR DESC
              ) hh
              WHERE rownum <= 10
              ORDER BY
                hh.DATA_OCORR
            ) hhh
            WHERE rownum = 1
        '''
        data_s = list(cursor_s.execute(sql))
        if len(data_s) == 0:
            return None
        else:
            return data_s[0][0]

    def get_hist_010(self, data):
        cursor_s = db_cursor_so()
        sql = '''
            SELECT
              h.*
            FROM HIST_010 h
            WHERE h.DATA_OCORR < %s
            ORDER BY
              h.DATA_OCORR
        '''
        cursor_s.execute(sql, [data])
        return self.iter_cursor(cursor_s)

    def insert_hist_010(self, row):
        cursor_f = db_cursor('default')
        sql = f'''
            INSERT INTO systextil_logs.hist_010
            ( area_producao
            , ordem_producao
            , periodo_producao
            , ordem_confeccao
            , tipo_historico
            , descricao_historico
            , tipo_ocorr
            , data_ocorr
            -- , hora_ocorr
            , usuario_rede
            , maquina_rede
            , aplicacao
            , nome_programa
            , usuario_sistema
            , grupo_maquina
            , tipo_ordem
            , codigo_empresa
            , codigo_estagio
            )
            VALUES
            ( {row["area_producao"]}
            , {row["ordem_producao"]}
            , {row["periodo_producao"]}
            , {row["ordem_confeccao"]}
            , {row["tipo_historico"]}
            , '{row["descricao_historico"]}'
            , '{row["tipo_ocorr"]}'
            , '{row["data_ocorr"]}'
            -- , '{row["hora_ocorr"]}'
            , '{row["usuario_rede"]}'
            , '{row["maquina_rede"]}'
            , '{row["aplicacao"]}'
            , '{row["nome_programa"]}'
            , '{row["usuario_sistema"]}'
            , '{row["grupo_maquina"]}'
            , {row["tipo_ordem"]}
            , {row["codigo_empresa"]}
            , {row["codigo_estagio"]}
            )
        '''
        cursor_f.execute(sql)

    def none_0(self, valor):
        return 0 if valor is None else valor

    def none_str_empty(self, valor):
        return '' if valor is None else valor

    def n_none_0(self, row, campos):
        for campo in campos:
            row[campo] = self.none_0(row[campo])

    def n_none_str_empty(self, row, campos):
        for campo in campos:
            row[campo] = self.none_str_empty(row[campo])

    def trata_none(self, row):
        self.n_none_0(
            row,
            [
                'area_producao',
                'ordem_producao',
                'periodo_producao',
                'ordem_confeccao',
                'tipo_historico',
                'tipo_ordem',
                'codigo_empresa',
                'codigo_estagio'
            ]
        )
        self.n_none_str_empty(
            row,
            [
                'descricao_historico',
                'tipo_ocorr',
                'data_ocorr',
                # 'hora_ocorr',
                'usuario_rede',
                'maquina_rede',
                'aplicacao',
                'nome_programa',
                'usuario_sistema',
                'grupo_maquina'
            ]
        )

    def del_hist_010(self, data):
        cursor_s = db_cursor_so()
        sql = '''
            DELETE FROM HIST_010 h
            WHERE h.DATA_OCORR <= %s
        '''
        cursor_s.execute(sql, [data])

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        try:
            data = self.get_last_hist_010_data()
            self.my_println(f"data {data}")

            ics = self.get_hist_010(data)

            def generator_list_echo(mylist):
                for i in mylist:
                    yield i
                while True:
                    yield i

            count = 0
            divisores = generator_list_echo([5, 10, 20, 50, 100])
            divisor = next(divisores)
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
                self.insert_hist_010(row)

                if (count % divisor) == 0:
                    divisor = next(divisores)
                    self.my_print(str(count))
                    self.my_print(' ')
                if count >= self.__MAX_TASKS:
                    can_break = True

            self.my_println(f"{count} registros copiados")

            if ult_data_ocorr is not None:
                self.my_println(f"ult_data_ocorr {ult_data_ocorr}")
                self.del_hist_010(ult_data_ocorr)

        except Exception as e:
            raise CommandError('Erro movendo HIST_010 "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
