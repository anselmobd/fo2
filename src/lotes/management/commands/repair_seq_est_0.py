import datetime
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.utils import timezone

from fo2.models import rows_to_dict_list_lower
import logistica.models as models


class Command(BaseCommand):
    help = 'Repair zeroed SEQUENCIA_ESTAGIO field in PCPC_040 TABLE.'

    def handle(self, *args, **options):
        try:
            cursor = connections['so'].cursor()

            # get lotes com SEQUENCIA_ESTAGIO zerado e mais de um estágio
            sql_get = '''
                SELECT
                    r.PERIODO_PRODUCAO PERIODO
                  , r.ORDEM_CONFECCAO OC
                FROM (
                  SELECT DISTINCT
                    le.PERIODO_PRODUCAO
                  , le.ORDEM_CONFECCAO
                  , count(*)
                  FROM pcpc_040 le
                  WHERE le.SEQUENCIA_ESTAGIO = 0
                  GROUP BY
                    le.PERIODO_PRODUCAO
                  , le.ORDEM_CONFECCAO
                  HAVING
                    count(*) > 1
                  ORDER BY
                    le.PERIODO_PRODUCAO
                  , le.ORDEM_CONFECCAO
                ) r
                WHERE rownum <= 100
            '''
            cursor.execute(sql_get)
            lotes = rows_to_dict_list_lower(cursor)
            # self.stdout.write('len(lotes) = {}'.format(len(lotes)))
            # pprint(lotes)

            # get new value to SEQUENCIA_ESTAGIO and ROWIDs
            sql_seq = '''
                SELECT
                  ROW_NUMBER() OVER (
                    PARTITION BY le.ORDEM_CONFECCAO ORDER BY le.ROWID
                  ) SEQ
                , le.ROWID RID
                FROM pcpc_040 le
                WHERE le.PERIODO_PRODUCAO = %s
                  AND le.ORDEM_CONFECCAO = %s
                ORDER BY
                  le.ROWID
            '''
            for lote in lotes:
                # self.stdout.write(str([lote['periodo'], lote['oc']]))
                self.stdout.write(str(lote))
                cursor.execute(sql_seq, [lote['periodo'], lote['oc']])
                seqs = rows_to_dict_list_lower(cursor)
                # self.stdout.write('len(seqs) = {}'.format(len(seqs)))
                # pprint(seqs)

                sql_setseq = '''
                    UPDATE pcpc_040 le
                    SET
                      le.SEQUENCIA_ESTAGIO = %s
                    WHERE le.ROWID = %s
                '''
                for seq in seqs:
                    # self.stdout.write(str([seq['rid'], seq['seq']]))
                    self.stdout.write(str(seq))
                    cursor.execute(sql_setseq, [seq['seq'], seq['rid']])

        except Exception as e:
            raise CommandError(
                'Error repairing SEQUENCIA_ESTAGIO ({})'.format(e))
