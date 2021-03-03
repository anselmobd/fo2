import datetime
import re
from pprint import pprint, pformat

from django.core.management.base import BaseCommand, CommandError
from django.db import connections

import produto.queries

import estoque.queries
from estoque.functions import ajuste_por_inventario


class Command(BaseCommand):
    help = 'Ajuste por inventário no Systêxtil'

    def my_println(self, text='', v=1):
        self.my_print(text, ending='\n', v=v)

    def my_print(self, text='', ending='', v=1):
        if v <= self.verbosity:
            self.stdout.write(text, ending=ending)
            self.stdout.flush()

    def add_arguments(self, parser):
        parser.add_argument('dep', help='101, 102 ou 231')
        parser.add_argument(
            'refmod',
            help='5 caracteres de referência ou menos que 5 para modelo')
        parser.add_argument('cor', help='6 caracteres', nargs='?')
        parser.add_argument('tam', help='1 a 3 caracteres', nargs='?')
        parser.add_argument('qtd', type=int, help='quantidade inventariada')
        parser.add_argument('data', help='data do inventário (AAAA-MM-DD)')
        parser.add_argument('hora', help='hora do inventário (HHhMM)')
        parser.add_argument(
            '-f', '--force',
            action="store_true",
            help='força ajuste do dia, mesmo se já houver')
        parser.add_argument(
            '-c', '--check',
            action="store_true",
            help='checa se o inventário confirma o estoque')
        parser.add_argument(
            '-j', '--jump',
            type=open,
            help='arquivo com ref cor tam que não devem ser afetados')
        parser.add_argument(
            '-d', '--delete',
            action="store_true",
            help='apaga inventários desse item nessa data/hora')

    def print_cmd_line(self, *cmd_line, v=1):
        msg = ' '.join(['{}']*len(cmd_line))
        self.my_println(msg.format(*cmd_line), v=v)

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']

        self.my_println('---', v=2)
        self.my_println('{}'.format(datetime.datetime.now()), v=2)

        dep = options['dep']
        refmod = options['refmod']
        cor = options['cor']
        tam = options['tam']
        qtd = options['qtd']
        data = options['data']
        hora = options['hora']
        force = options['force']
        check = options['check']
        jump = options['jump']
        delete = options['delete']

        if jump:
            jump_itens = []
            with jump as fp:
                for line in fp:
                    res = re.findall(r'\w+', line)
                    jump_itens.append(res[:3])

        itens = []

        cursor = connections['so'].cursor()

        if len(refmod) != 5:
            modelo = refmod
            itens_list = estoque.queries.estoque_deposito_ref_modelo(
                cursor, dep, modelo=modelo)
            for row in itens_list:
                itens.append({
                    'ref': row['ref'],
                    'cor': row['cor'],
                    'tam': row['tam'],
                })
        else:
            ref = refmod

            if cor is None:
                cores_list = produto.queries.ref_cores(cursor, ref)
                if len(cores_list) != 0:
                    cores = [row['COR'] for row in cores_list]
            else:
                cores = [cor]

            if tam is None:
                tamanhos_list = produto.queries.ref_tamanhos(cursor, ref)
                if len(tamanhos_list) != 0:
                    tamanhos = [row['TAM'] for row in tamanhos_list]
            else:
                tamanhos = [tam]

            for cor_ in cores:
                for tam_ in tamanhos:
                    itens.append({
                        'ref': ref,
                        'cor': cor_,
                        'tam': tam_,
                    })

        if len(itens) == 0:
            itens.append({
                'ref': ref,
                'cor': cor,
                'tam': tam,
            })

        for item in itens:
            if jump:
                jump_item = [
                    item['ref'],
                    item['cor'],
                    item['tam'],
                    ]
                if jump_item in jump_itens:
                    continue

            cmd_line_tuple = (
                dep,
                item['ref'],
                item['cor'],
                item['tam'],
                qtd,
                data,
                hora,
                )

            self.print_cmd_line(*cmd_line_tuple)

            try:
                sucesso, mensagem, infos = ajuste_por_inventario(
                    cursor,
                    dep,
                    item['ref'],
                    item['tam'],
                    item['cor'],
                    qtd,
                    data,
                    hora,
                    force,
                    check,
                    delete,
                )
                if sucesso:
                    self.my_println('Sucesso [{}]'.format(mensagem))
                else:
                    if self.verbosity == 0:
                        self.print_cmd_line(*cmd_line_tuple[1:5], v=0)
                    self.my_println('Erro [{}]'.format(mensagem))
                self.my_println(pformat(infos), v=2)
            except Exception as e:
                raise CommandError('Exceção [{}]'.format(mensagem))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'), v=2)
