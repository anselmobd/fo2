import sys
import datetime
from pprint import pprint, pformat

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, connections

import base.models
from fo2.settings import DEBUG
from utils.functions.models import rows_to_dict_list_lower

import lotes.models as models


class Command(BaseCommand):
    help = 'Move BASI_010 do banco do systextil para o banco da intranet'
    __MAX_TASKS = 100

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

    def get_last_basi_010_data_hora(self):
        cursor_s = connections['so'].cursor()
        sql = '''
            SELECT
              hh.*
            FROM
            ( SELECT
                h.DATA_OCORR
              , h.HORA_OCORR
              FROM HIST_010 h
              ORDER BY
                h.DATA_OCORR DESC
              , h.HORA_OCORR DESC
            ) hh
            WHERE rownum = 1
        '''
        data_s = list(cursor_s.execute(sql))
        if len(data_s) == 0:
            return None, None
        else:
            return data_s[0]

    def get_basi_010(self, data, hora):
        cursor_s = connections['so'].cursor()
        sql = '''
            SELECT
              h.*
            FROM HIST_010 h
            WHERE h.DATA_OCORR < %s
              AND h.HORA_OCORR < %s
        '''
        cursor_s.execute(sql, [data, hora])
        return self.iter_cursor(cursor_s)

    def insert_basi_010(self, row):
        cursor_f = connections['default'].cursor()
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
            , hora_ocorr
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
            , '{row["hora_ocorr"]}'
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
                'hora_ocorr',
                'usuario_rede',
                'maquina_rede',
                'aplicacao',
                'nome_programa',
                'usuario_sistema',
                'grupo_maquina'
            ]
        )

    def del_basi_010(self, data, hora):
        cursor_s = connections['so'].cursor()
        sql = '''
            DELETE FROM HIST_010 h
            WHERE h.DATA_OCORR < %s
              AND h.HORA_OCORR < %s
        '''
        cursor_s.execute(sql, [data, hora])

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        if DEBUG:
            self.my_println('Só roda em produção')
            return

        try:
            data, hora = self.get_last_basi_010_data_hora()
            self.my_println(f"data {data}")
            self.my_println(f"hora {hora}")

            ics = self.get_basi_010(data, hora)

            count = 0
            for row in ics:
                count += 1
                self.trata_none(row)
                self.my_print(".")
                self.insert_basi_010(row)
            self.my_println(f"{count} registros copiados")

            self.del_basi_010(data, hora)

        except Exception as e:
            raise e
            raise CommandError('Erro movendo BASI_010 "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
