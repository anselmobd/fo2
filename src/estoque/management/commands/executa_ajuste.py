from pprint import pprint
import datetime

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Executa transação no Systêxtil'

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def add_arguments(self, parser):
        parser.add_argument('dep', help='101, 102 ou 231', nargs=1)
        parser.add_argument('ref', help='5 caracteres', nargs=1)
        parser.add_argument('cor', help='6 caracteres', nargs=1)
        parser.add_argument('tam', help='1 a 3 caracteres', nargs=1)
        parser.add_argument('qtd', type=int, nargs=1,
                            help='Indica a quantidade transacionada')
        parser.add_argument('doc', help='número do documento', nargs=1)

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))
        try:
            pass
        except Exception as e:
            raise CommandError(
                'Erro executando transação no Systêxtil "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
