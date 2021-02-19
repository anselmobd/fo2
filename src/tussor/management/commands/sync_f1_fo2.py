import datetime
import re
from pprint import pprint, pformat

from django.core.management.base import BaseCommand, CommandError
from django.db import connections

import produto.queries

import estoque.queries
from estoque.functions import ajuste_por_inventario


class Command(BaseCommand):
    help = 'Sincroniza de F1 para Fo2'

    def my_println(self, text='', v=1):
        self.my_print(text, ending='\n', v=v)

    def my_print(self, text='', ending='', v=1):
        if v <= self.verbosity:
            self.stdout.write(text, ending=ending)
            self.stdout.flush()

    def add_arguments(self, parser):
        parser.add_argument('tabela', help='cli ou dup', nargs='?')
        parser.add_argument('qtd', type=int, help='quantidade de registros', nargs='?')

    def basic_params(self):
        self.verbosity = self.options['verbosity']

    def params(self):
        self.tabela = self.options['tabela']
        self.qtd = self.options['qtd']

        dic_tabelas = {
            None: ('cli', 'dup'),
            'cli': ('cli', ),
            'dup': ('dup', ),
        }

        self.tabelas = dic_tabelas[self.tabela]
        self.my_println(f'tabelas = {self.tabelas}')

        if self.qtd:
            self.my_println(f'qtd = {self.qtd}')

    def sync_cli(self):
        self.my_println('sync_cli', v=2)

    def sync_dup(self):
        self.my_println('sync_dup', v=2)

    def exec(self):
        if 'cli' in self.tabelas:
            self.sync_cli()
        if 'dup' in self.tabelas:
            self.sync_dup()

    def handle(self, *args, **options):
        self.options = options
        self.basic_params()

        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        try:
            self.params()
            self.exec()
        except Exception as e:
            raise CommandError(f"Erro! <{e}>")

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
