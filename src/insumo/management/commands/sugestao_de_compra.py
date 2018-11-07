import re
from datetime import datetime, timedelta
from pprint import pprint
import pytz
import time

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.db import connections

import insumo.models as models
from insumo.views import MapaPorInsumo_dados
from insumo.queries import insumos_cor_tamanho_usados


class Command(BaseCommand):
    help = 'Monta tabela de sugestão de compras por insumo.'
    __MAX_TASKS = 10
    __cursor = None

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

    @property
    def cursor(self):
        if self.__cursor is None:
            self.__cursor = connections['so'].cursor()
        return self.__cursor

    def sugestao_de_insumo(self, nivel, ref, cor, tam, limite):
        item = '{}.{}.{}.{}'.format(nivel, ref, cor, tam)

        sc = models.SugestaoCompra.objects.filter(
            nivel=nivel,
            referencia=ref,
            tamanho=tam,
            cor=cor,
        ).order_by('-data').first()

        ultima_sug = []
        if sc:
            if limite == 'd':
                delta_limite = timedelta(hours=24)
            elif limite == 'h':
                delta_limite = timedelta(minutes=180)
            else:  # elif limite == 'm':
                delta_limite = timedelta(minutes=1)
            if sc.data > timezone.now() - delta_limite:
                if self.verbosity > 1:
                    self.my_println('{} Sugestão recente'.format(item))
                return False

            scd = models.SugestaoCompraDatas.objects.filter(
                sugestao=sc).order_by('data_compra').values()
            for data in scd:
                ultima_sug.append({
                    'QUANT': data['qtd'],
                    'SEMANA_COMPRA': data['data_compra'],
                    'SEMANA_RECEPCAO': data['data_recepcao'],
                })

        datas = MapaPorInsumo_dados(self.cursor, nivel, ref, cor, tam)
        data_sug = datas['data_sug']
        time.sleep(1)

        if sc and ultima_sug == data_sug:
            self.my_println('{} Sugestão inalterada'.format(item))
            sc.data = timezone.now()
            sc.save()
        else:
            self.my_println('{} Nova sugestão'.format(item))
            sc = models.SugestaoCompra()
            sc.nivel = nivel
            sc.referencia = ref
            sc.tamanho = tam
            sc.ordem_tamanho = 0
            sc.cor = cor
            sc.data = timezone.now()
            sc.save()

            for sugestao in data_sug:
                scd = models.SugestaoCompraDatas()
                scd.sugestao = sc
                scd.data_compra = sugestao['SEMANA_COMPRA']
                scd.data_recepcao = sugestao['SEMANA_RECEPCAO']
                scd.qtd = sugestao['QUANT']
                scd.save()

        return True

    def handle(self, *args, **kwargs):
        self.my_println('---')
        self.my_println('{}'.format(datetime.now()))
        self.verbosity = kwargs['verbosity']

        nivel = kwargs['nivel_ou_tipo']
        ref = kwargs['referencia']
        cor = kwargs['cor']
        tam = kwargs['tamanho']
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
                    limite = 'h'

                elif nivel == 'n':
                    self.my_println('Insumos não utilizados em estruturas')
                    insumos = insumos_cor_tamanho_usados(self.cursor, uso='N')
                    limite = 'd'

                elif nivel == 't':
                    self.my_println('Todos os insumos')
                    insumos = insumos_cor_tamanho_usados(self.cursor)
                    limite = 'd'

                count_task = 0
                for insumo in insumos:
                    nivel = insumo['nivel']
                    ref = insumo['ref']
                    cor = insumo['cor']
                    tam = insumo['tam']
                    if self.sugestao_de_insumo(nivel, ref, cor, tam, limite):
                        count_task += 1
                    if count_task >= self.__MAX_TASKS:
                        self.my_println('Chegou ao limite de tarefas')
                        break

            elif conta_none == 0:
                self.valid_1A(ref, 5, 'Referencia')
                self.valid_1A(cor, 6, 'Cor')
                self.valid_1A(tam, '1,3', 'Tamanho')

                self.sugestao_de_insumo(nivel, ref, cor, tam, 'm')

        except Exception as e:
            raise CommandError(
                'Error montando sugestão de compras "{}"'.format(e))

        self.my_println(format(datetime.now(), '%H:%M:%S.%f'))
