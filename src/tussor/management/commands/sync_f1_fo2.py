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
        parser.add_argument('tabela', help='cli ou dup')
        parser.add_argument('qtd', type=int, help='quantidade de registros')

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']

        self.my_println('---', v=2)
        self.my_println('{}'.format(datetime.datetime.now()), v=2)

        tabela = options['tabela']
        qtd = options['qtd']

        try:
            pass
        except Exception as e:
            raise CommandError(f"Exceção [{e}]")

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'), v=2)
