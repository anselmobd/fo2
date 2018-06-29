import sys
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.db import connections


class Command(BaseCommand):
    help = 'Mostra o count(*) de todas as tabelas do Systêxtil'

    def handle(self, *args, **options):
        try:
            systextil_conn = connections['so']
            tables = systextil_conn.introspection.table_names()
            cursor = systextil_conn.cursor()

            tbl_counts = {}
            sql = '''
                SELECT
                  count(*)
                FROM {table}
            '''
            for table in tables:
                # print(sql.format(table=table))
                cursor.execute(sql.format(table=table))
                row = cursor.fetchone()
                # print(row[0])
                tbl_counts[table] = row[0]
                print('{:12} {}'.format(row[0], table))

            # pprint(tbl_counts)

        except Exception as e:
            raise CommandError('Error counting in tables. {}'.format(e))
