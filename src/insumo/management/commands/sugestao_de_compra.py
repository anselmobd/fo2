import sys
import datetime
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, connections

from fo2.models import rows_to_dict_list_lower
import lotes.models as models


class Command(BaseCommand):
    help = 'Monta tabela de sugestão de compras por insumo.'
    __MAX_TASKS = 100

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def iter_cursor(self, cursor):
        columns = [i[0].lower() for i in cursor.description]
        for row in cursor:
            dict_row = dict(zip(columns, row))
            yield dict_row

    def get_someting(self):
        cursor_s = connections['so'].cursor()
        sql = '''
            SELECT
              1
            FROM DUAL
        '''
        cursor_s.execute(sql)
        return self.iter_cursor(cursor_s)

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))
        try:

            # pega xyz
            ixyz = self.get_someting()

            count_task = 0
            while count_task < self.__MAX_TASKS:

                try:
                    row_xyz = next(ixyz)
                    field = row_xyz['field']
                except StopIteration:
                    pass

        except Exception as e:
            raise CommandError(
                'Error montando sugestão de compras "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
