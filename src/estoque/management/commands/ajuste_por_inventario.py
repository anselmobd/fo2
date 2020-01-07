from pprint import pprint, pformat
import datetime

from django.db import connections
from django.core.management.base import BaseCommand, CommandError

import produto.queries

from estoque.views import ajuste_por_inventario


class Command(BaseCommand):
    help = 'Ajuste por inventário no Systêxtil'

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def add_arguments(self, parser):
        parser.add_argument('dep', help='101, 102 ou 231')
        parser.add_argument('ref', help='5 caracteres')
        parser.add_argument('cor', help='6 caracteres')
        parser.add_argument('tam', help='1 a 3 caracteres', nargs='?')
        parser.add_argument('qtd', type=int, help='quantidade inventariada')
        parser.add_argument('data', help='data do inventário (AAAA-MM-DD)')
        parser.add_argument('hora', help='hora do inventário (HHhMM)')

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        dep = options['dep']
        ref = options['ref']
        cor = options['cor']
        tam = options['tam']
        qtd = options['qtd']
        data = options['data']
        hora = options['hora']

        itens = []

        if tam is None:
            cursor = connections['so'].cursor()

            tamanhos_list = produto.queries.ref_tamanhos(cursor, ref)
            if len(tamanhos_list) != 0:
                for row in tamanhos_list:
                    itens.append({
                        'ref': ref,
                        'cor': cor,
                        'tam': row['TAM'],
                    })

        if len(itens) == 0:
            itens.append({
                'ref': ref,
                'cor': cor,
                'tam': tam,
            })

        for item in itens:
            self.my_println(
                '{} {} {} {} {} {} {}'.format(
                    dep,
                    item['ref'],
                    item['tam'],
                    item['cor'],
                    qtd,
                    data,
                    hora,
                )
            )
            try:
                # _ = 1/0
                sucesso, mensagem, infos = ajuste_por_inventario(
                    dep,
                    item['ref'],
                    item['tam'],
                    item['cor'],
                    qtd,
                    data,
                    hora,
                )
            except Exception as e:
                sucesso = False
                mensagem = '{}'.format(e)
                infos = []

            if not sucesso:
                info_string = ''
                if len(infos) != 0:
                    info_string = '\n{}'.format(pformat(infos))
                raise CommandError(
                    'Erro [{}]{}'.format(mensagem, info_string))
            self.my_println(
                'Sucesso [{}]'.format(mensagem))

            self.my_println(pformat(infos))

            self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
