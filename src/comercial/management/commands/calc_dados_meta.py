import datetime
from pprint import pprint, pformat

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from fo2.connections import db_cursor_so

from utils.decorators import CacheGet

import comercial.queries


class Command(BaseCommand):
    help = 'Carrega no cache dados da meta do ano'

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        text = str(text)
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
            cursor = db_cursor_so()
            hoje = datetime.date.today()

            cg = CacheGet()
            msg_erro, meses, total = cg.get_result(
                comercial.queries.dados_meta_no_ano(cursor, hoje)
            )
            self.my_pprintln(cg.params)

            if msg_erro:
                self.my_println(msg_erro)
            else:
                self.my_pprintln(meses)
                self.my_pprintln(total)

        except Exception as e:
            raise CommandError(
                'Erro carregando no cache dados da meta do ano "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
