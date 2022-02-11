import datetime
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from fo2.connections import db_cursor_so

from utils.functions.models import rows_to_dict_list
from utils.functions.queries import debug_cursor_execute
import logistica.models as models


class Command(BaseCommand):
    help = 'Seting PRECO_MEDIO in level 1 products, when zeroed.'

    def handle(self, *args, **options):
        try:
            cursor = db_cursor_so()

            # get zeroed itens
            sql_get = '''
                SELECT
                  ptc.GRUPO_ESTRUTURA REF
                , ptc.SUBGRU_ESTRUTURA TAM
                , ptc.ITEM_ESTRUTURA COR
                FROM basi_010 ptc
                WHERE ptc.NIVEL_ESTRUTURA = 1
                  AND (  ptc.PRECO_MEDIO IS NULL
                      OR ptc.PRECO_MEDIO = 0
                      )
                  -- AND rownum = 1
            '''
            debug_cursor_execute(cursor, sql_get)
            zeroed_ori = rows_to_dict_list(cursor)
            # self.stdout.write('len(zeroed_ori) = {}'.format(len(zeroed_ori)))

            # set PRECO_MEDIO
            sql_set = '''
                UPDATE basi_010 ptc
                SET
                  ptc.PRECO_MEDIO = 2
                WHERE ptc.NIVEL_ESTRUTURA = 1
                  AND ptc.GRUPO_ESTRUTURA = %s
                  AND ptc.SUBGRU_ESTRUTURA = %s
                  AND ptc.ITEM_ESTRUTURA = %s
            '''
            for ori in zeroed_ori:
                # self.stdout.write(str([ori['REF'], ori['TAM'], ori['COR']]))
                debug_cursor_execute(cursor, sql_set, [ori['REF'], ori['TAM'], ori['COR']])

            debug_cursor_execute(cursor, sql_get)
            zeroed_new = rows_to_dict_list(cursor)

            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            for ori in zeroed_ori:
                if ori not in zeroed_new:
                    if date:
                        self.stdout.write(date)
                        date = None
                    self.stdout.write(str(ori))

        except Exception as e:
            raise CommandError('Error seting PRECO_MEDIO'.format(e))
