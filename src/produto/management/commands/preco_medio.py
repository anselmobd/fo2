import datetime
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.utils import timezone

from fo2.models import rows_to_dict_list
import logistica.models as models


class Command(BaseCommand):
    help = 'Seting PRECO_MEDIO in level 1 products, when zeroed.'

    def handle(self, *args, **options):
        try:
            cursor = connections['so'].cursor()

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
            cursor.execute(sql_get)
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
                cursor.execute(sql_set, [ori['REF'], ori['TAM'], ori['COR']])

            cursor.execute(sql_get)
            zeroed_new = rows_to_dict_list(cursor)

            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            for ori in zeroed_ori:
                if ori not in zeroed_new:
                    if date:
                        print(date)
                        date = None
                    self.stdout.write(str(ori))

        except Exception as e:
            raise CommandError('Error seting PRECO_MEDIO'.format(e))
