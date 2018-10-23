# import sys
import re
import datetime
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.db import connections

# from fo2.models import rows_to_dict_list_lower
# import lotes.models as models

from insumo.views import MapaPorInsumo_dados


class Command(BaseCommand):
    help = 'Monta tabela de sugestão de compras por insumo.'
    # __MAX_TASKS = 100

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    # def iter_cursor(self, cursor):
    #     columns = [i[0].lower() for i in cursor.description]
    #     for row in cursor:
    #         dict_row = dict(zip(columns, row))
    #         yield dict_row
    #
    # def get_someting(self):
    #     cursor_s = connections['so'].cursor()
    #     sql = '''
    #         SELECT
    #           1
    #         FROM DUAL
    #     '''
    #     cursor_s.execute(sql)
    #     return self.iter_cursor(cursor_s)

    def valid_1A(self, s, tam, descr):
        pat = re.compile(r"^[0-9A-Z]{%s}$" % (tam))
        if not pat.match(s):
            msg = "Valor de '{}' inválido: '{}'.".format(descr, s)
            raise Exception(msg)

    def conta_nao_None(self, name):
        if self.kwargs[name] is None:
            return 0
        else:
            return 1

    def add_arguments(self, parser):
        parser.add_argument(
            'nivel', help='nivel', choices=['2', '9'], nargs='?')
        parser.add_argument('referencia', help='5 caracteres', nargs='?')
        parser.add_argument('cor', help='6 caracteres', nargs='?')
        parser.add_argument('tamanho', help='1 a 3 caracteres', nargs='?')

    def handle(self, *args, **kwargs):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))
        self.kwargs = kwargs

        try:
            conta_parm = \
                self.conta_nao_None('nivel') + \
                self.conta_nao_None('referencia') + \
                self.conta_nao_None('cor') + \
                self.conta_nao_None('tamanho')
            if conta_parm % 4 != 0:
                msg = "Informe as 4 partes do código do item ou nada"
                raise Exception(msg)

            if conta_parm == 4:
                nivel = kwargs['nivel']
                ref = kwargs['referencia']
                cor = kwargs['cor']
                tam = kwargs['tamanho']
                self.valid_1A(ref, 5, 'Referencia')
                self.valid_1A(cor, 6, 'Cor')
                self.valid_1A(tam, '1,3', 'Tamanho')

                cursor = connections['so'].cursor()
                datas = MapaPorInsumo_dados(cursor, nivel, ref, cor, tam)
                pprint(datas['data_sug'])

            # pega xyz
            # ixyz = self.get_someting()
            #
            count_task = 0
            # while count_task < self.__MAX_TASKS:
            #
            #     try:
            #         row_xyz = next(ixyz)
            #         field = row_xyz['field']
            #     except StopIteration:
            #         pass
            #
        except Exception as e:
            raise CommandError(
                'Error montando sugestão de compras "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
