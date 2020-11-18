import datetime
from pprint import pprint, pformat

from django.core.management.base import BaseCommand, CommandError

import comercial.queries


class Command(BaseCommand):
    help = 'Carrega no cache dados da meta do ano'

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def my_pprintln(self, object):
        self.my_pprint(object, ending='\n')

    def my_pprint(self, object, ending=''):
        self.stdout.write(pformat(object), ending=ending)
        self.stdout.flush()

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        try:
            hoje = datetime.date.today()
            meses, total = comercial.queries.dados_meta_no_ano(hoje)
            self.my_pprintln(meses)
            self.my_pprintln(total)

        except Exception as e:
            raise CommandError(
                'Erro carregando no cache dados da meta do ano "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
