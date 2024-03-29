import datetime
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from fo2.connections import db_cursor_so

import logistica.models as models
from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute


class Command(BaseCommand):
    help = 'Copying CODIGO_FAMILIA from operation 21 to 33, when advanced.'

    def handle(self, *args, **options):
        try:
            cursor = db_cursor_so()

            # get lotes a atualizar família do estágio 33
            sql_get = '''
                SELECT
                  l21.CODIGO_FAMILIA
                , l21.PERIODO_PRODUCAO
                , l21.ORDEM_CONFECCAO
                FROM PCPC_040 l21
                JOIN pcpc_040 l33
                  ON l33.PERIODO_PRODUCAO = l21.PERIODO_PRODUCAO
                 AND l33.ORDEM_CONFECCAO = l21.ORDEM_CONFECCAO
                JOIN pcpc_020 o
                  ON o.ORDEM_PRODUCAO = l21.ORDEM_PRODUCAO
                WHERE o.ALTERNATIVA_PECA = 1
                  AND l21.PERIODO_PRODUCAO = o.PERIODO_PRODUCAO
                  AND l21.CODIGO_ESTAGIO = 21
                  AND l21.CODIGO_FAMILIA <> 0
                  AND l33.CODIGO_ESTAGIO = 33
                  AND l33.CODIGO_FAMILIA = 0
                  AND (  l33.QTDE_PECAS_PROD <> 0
                      OR l33.QTDE_CONSERTO <> 0
                      OR l33.QTDE_PECAS_2A <> 0
                      OR l33.QTDE_PERDAS <> 0
                      )
            '''
            debug_cursor_execute(cursor, sql_get)
            lotes_ori = dictlist(cursor)
            # self.stdout.write('len(lotes_ori) = {}'.format(len(lotes_ori)))

            # set CODIGO_FAMILIA
            sql_set = '''
                UPDATE PCPC_040 l
                SET
                  l.CODIGO_FAMILIA = %s
                WHERE l.PERIODO_PRODUCAO = %s
                  AND l.ORDEM_CONFECCAO = %s
                  AND l.CODIGO_ESTAGIO = 33
            '''
            for ori in lotes_ori:
                # self.stdout.write(str(
                #    [ori['CODIGO_FAMILIA'], ori['PERIODO_PRODUCAO'],
                #     ori['ORDEM_CONFECCAO']]))
                debug_cursor_execute(
                    cursor, 
                    sql_set,
                    [ori['CODIGO_FAMILIA'], ori['PERIODO_PRODUCAO'],
                     ori['ORDEM_CONFECCAO']])

            debug_cursor_execute(cursor, sql_get)
            lotes_new = dictlist(cursor)

            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            for ori in lotes_ori:
                if ori not in lotes_new:
                    if date:
                        self.stdout.write(date)
                        date = None
                    self.stdout.write(str(ori))

        except Exception as e:
            raise CommandError('Error copying CODIGO_FAMILIA'.format(e))
