# import sys
import re
from datetime import datetime
from pprint import pprint
import pytz

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.db import connections

import insumo.models as models
from insumo.views import MapaPorInsumo_dados
from insumo.queries import insumos_cor_tamanho_usados


class Command(BaseCommand):
    help = 'Monta tabela de sugestão de compras por insumo.'
    # __MAX_TASKS = 100

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
            choices=['2', '9', 'e', 't'], nargs='?')
        parser.add_argument('referencia', help='5 caracteres', nargs='?')
        parser.add_argument('cor', help='6 caracteres', nargs='?')
        parser.add_argument('tamanho', help='1 a 3 caracteres', nargs='?')

    def sugestao_de_insumo(self, nivel, ref, cor, tam):
        self.my_println('Insumo {}.{}.{}.{}'.format(
            nivel, ref, cor, tam))

        cursor = connections['so'].cursor()
        datas = MapaPorInsumo_dados(cursor, nivel, ref, cor, tam)
        data_sug = datas['data_sug']
        # pprint(data_sug)

        sc = models.SugestaoCompra.objects.filter(
            nivel=nivel,
            referencia=ref,
            tamanho=tam,
            cor=cor,
        ).order_by('-data').first()

        ultima_sug = []
        if sc:
            # print(sc.id)
            scd = models.SugestaoCompraDatas.objects.filter(
                sugestao=sc).order_by('data_compra').values()
            for data in scd:
                # pprint(data)
                ultima_sug.append({
                    'QUANT': data['qtd'],
                    'SEMANA_COMPRA': data['data_compra'],
                    'SEMANA_RECEPCAO': data['data_recepcao'],
                })
            # pprint(ultima_sug)
            # print(ultima_sug == data_sug)

        if ultima_sug == data_sug:
            self.my_println('Sugestão inalterada')
        else:
            self.my_println('Nova sugestão')
            sc = models.SugestaoCompra()
            sc.nivel = nivel
            sc.referencia = ref
            sc.tamanho = tam
            sc.ordem_tamanho = 0
            sc.cor = cor
            sc.data = timezone.now()
            sc.save()
            # print(sc.id)

            for sugestao in data_sug:
                # pprint(sugestao)
                scd = models.SugestaoCompraDatas()
                scd.sugestao = sc
                scd.data_compra = sugestao['SEMANA_COMPRA']
                scd.data_recepcao = sugestao['SEMANA_RECEPCAO']
                scd.qtd = sugestao['QUANT']
                scd.save()
                # print(scd.id)

    def handle(self, *args, **kwargs):
        self.my_println('---')
        self.my_println('{}'.format(datetime.now()))

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
                if nivel == 'e':
                    self.my_println('Insumos de estruturas')
                    insumos = [
                        {'nivel': '2',
                         'ref': 'AM001',
                         'cor': '0000BR',
                         'tam': '0BR',
                         },
                        {'nivel': '2',
                         'ref': 'MA002',
                         'cor': '0000BR',
                         'tam': 'UNI',
                         },
                        {'nivel': '2',
                         'ref': 'MA002',
                         'cor': '0000PR',
                         'tam': 'UNI',
                         },
                        {'nivel': '9',
                         'ref': 'CA001',
                         'cor': '0000PR',
                         'tam': 'UNI',
                         },
                    ]

                elif nivel == 't':
                    self.my_println('Todos os insumos')

                    cursor_ = connections['so'].cursor()
                    insumos = insumos_cor_tamanho_usados(
                        cursor_, 4)

                for insumo in insumos:
                    nivel = insumo['nivel']
                    ref = insumo['ref']
                    cor = insumo['cor']
                    tam = insumo['tam']
                    self.sugestao_de_insumo(nivel, ref, cor, tam)

            elif conta_none == 0:
                self.valid_1A(ref, 5, 'Referencia')
                self.valid_1A(cor, 6, 'Cor')
                self.valid_1A(tam, '1,3', 'Tamanho')

                self.sugestao_de_insumo(nivel, ref, cor, tam)

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

        except Exception as e:
            raise CommandError(
                'Error montando sugestão de compras "{}"'.format(e))

        self.my_println(format(datetime.now(), '%H:%M:%S.%f'))
