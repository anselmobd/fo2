from pprint import pprint
import datetime

from django.core.management.base import BaseCommand, CommandError

from estoque.views import executa_ajuste


class Command(BaseCommand):
    help = 'Executa transação no Systêxtil'

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def add_arguments(self, parser):
        parser.add_argument('dep', help='101, 102 ou 231')
        parser.add_argument('ref', help='5 caracteres')
        parser.add_argument('cor', help='6 caracteres')
        parser.add_argument('tam', help='1 a 3 caracteres')
        parser.add_argument('qtd', type=int,
                            help='Indica a quantidade transacionada')
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

        self.my_println(
            '%s %s %s %s %s %s %s' % (dep, ref, cor, tam, qtd, data, hora))

        try:
            pass
        except Exception as e:
            raise CommandError(
                'Erro executando transação no Systêxtil "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
