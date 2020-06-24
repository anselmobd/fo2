import sys
import re
from datetime import datetime, timedelta
from pprint import pprint
import pytz
import time

from django.utils import timezone
from django.db import connections
from django.core.management.base import BaseCommand, CommandError

import insumo.models as models
from insumo.functions import mapa_por_insumo_dados
from insumo.queries import insumos_cor_tamanho_usados, insumos_cor_tamanho


class Command(BaseCommand):
    help = 'Guarda em cache o mapa de sugestão de compras por insumo.'
    _MAX_TASKS = sys.maxsize
    _STEP_SLEEP = 0.5
    _cursor = None

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def valid_1A(self, s, tam, descr):
        pat = re.compile(r"^[0-9A-Z]{%s}$" % (tam))
        if not pat.match(s):
            msg = "Valor de '{}' inválido: '{}'.".format(descr, s)
            raise Exception(msg)

    def countNone(self, *values):
        count = 0
        for value in values:
            if value is None:
                count += 1
        return count

    def add_arguments(self, parser):
        parser.add_argument(
            'nivel_ou_tipo', help='nivel ou tipo',
            choices=['2', '9', 'u', 'n', 't'], nargs='?')
        parser.add_argument('referencia', help='5 caracteres', nargs='?')
        parser.add_argument('cor', help='6 caracteres', nargs='?')
        parser.add_argument('tamanho', help='1 a 3 caracteres', nargs='?')
        parser.add_argument(
            '-t', '--max-tasks', type=int, nargs='?',
            help='Indica o número máximo de cálculos que serão executado '
                 '(utilizado para testar a rotina)')

    @property
    def cursor(self):
        if self._cursor is None:
            self._cursor = connections['so'].cursor()
        return self._cursor

    def handle(self, *args, **kwargs):
        self.my_println('{}'.format(datetime.now()))
        self.my_println('---')

        self.verbosity = kwargs['verbosity']

        nivel = kwargs['nivel_ou_tipo']
        ref = kwargs['referencia']
        cor = kwargs['cor']
        tam = kwargs['tamanho']
        if kwargs['max_tasks'] is not None:
            self._MAX_TASKS = kwargs['max_tasks']

        try:
            conta_none = self.countNone(nivel, ref, cor, tam)
            if conta_none % 3 != 0:
                raise Exception(
                    "Informe as 4 partes do código do item "
                    "ou o tipo de execução")

            if conta_none == 3:
                if nivel == 'u':
                    self.my_println('Insumos utilizados em estruturas')
                    insumos = insumos_cor_tamanho_usados(self.cursor, uso='U')

                elif nivel == 'n':
                    self.my_println('Insumos não utilizados em estruturas')
                    insumos = insumos_cor_tamanho_usados(self.cursor, uso='N')

                elif nivel == 't':
                    self.my_println('Todos os insumos')
                    insumos = insumos_cor_tamanho(
                        self.cursor, qtd_itens=str(self._MAX_TASKS))

                count_task = 0
                for insumo in insumos:
                    nivel = insumo['nivel']
                    ref = insumo['ref']
                    cor = insumo['cor']
                    tam = insumo['tam']
                    self.my_println('{}.{}.{}.{}'.format(
                        nivel, ref, cor, tam))
                    mapa_por_insumo_dados(
                          self.cursor, nivel, ref, cor, tam, calc=True)
                    time.sleep(self._STEP_SLEEP)
                    count_task += 1
                    if count_task == self._MAX_TASKS:
                        self.my_println(
                            'atingiu o limite de {} tarefas'.format(
                                self._MAX_TASKS))
                        break

            elif conta_none == 0:
                self.valid_1A(ref, 5, 'Referencia')
                self.valid_1A(cor, 6, 'Cor')
                self.valid_1A(tam, '1,3', 'Tamanho')

                mapa_por_insumo_dados(
                    self.cursor, nivel, ref, cor, tam, calc=True)

        except Exception as e:
            raise CommandError(
                'Error atualizando o cache de mapa de compras "{}"'.format(e))

        self.my_println(format(datetime.now(), '%H:%M:%S.%f'))
