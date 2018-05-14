import datetime
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.utils import timezone

from fo2.models import rows_to_dict_list_lower
import logistica.models as models


class Command(BaseCommand):
    help = 'BUG CORRECT TO: ' \
        'Repair zeroed SEQUENCIA_ESTAGIO field in PCPC_040 TABLE.'

    def handle(self, *args, **options):
        self.stdout.write('---\n{}'.format(datetime.datetime.now()))
        # try:
        cursor = connections['so'].cursor()

        # get primeira OP com mais de um padrão de SEQUENCIA_ESTAGIO
        sql_get = '''
            SELECT
              oo.*
            FROM (
              SELECT
                oe.OP
              , count(*)
              FROM (
                SELECT DISTINCT
                  le.ORDEM_PRODUCAO OP
                , le.SEQUENCIA_ESTAGIO SEQEST
                , le.CODIGO_ESTAGIO
                FROM pcpc_040 le
                WHERE le.SEQUENCIA_ESTAGIO = 1
                --  AND le.ORDEM_PRODUCAO = 1637
              ) oe
              GROUP BY
                oe.OP
              , oe.SEQEST
              HAVING
                count(*) > 1
              ORDER BY
                2 DESC
              , 1
            ) oo
            WHERE rownum <= 10
        '''
        cursor.execute(sql_get)
        ops = rows_to_dict_list_lower(cursor)
        # self.stdout.write('len(ops) = {}'.format(len(ops)))
        # self.stdout.write('op = {}'.format(ops[0]['op']))
        for opr in ops:
            op = opr['op']
            self.stdout.write('--- op = {}'.format(op))

            # get lotes dessa OP
            sql_get = '''
                SELECT DISTINCT
                  le.PERIODO_PRODUCAO PERIODO
                , le.ORDEM_CONFECCAO OC
                FROM pcpc_040 le
                WHERE le.ORDEM_PRODUCAO = %s
                --  AND rownum = 1
                ORDER BY
                  le.PERIODO_PRODUCAO
                , le.ORDEM_CONFECCAO
            '''
            cursor.execute(sql_get, [op])
            lotes = rows_to_dict_list_lower(cursor)
            self.stdout.write('len(lotes) = {}'.format(len(lotes)))
            # pprint(lotes)

            # get new value to SEQUENCIA_ESTAGIO based in
            # SEQ_OPERACAO and ROWIDs
            sql_seq = '''
                SELECT
                  s.*
                FROM (
                  SELECT
                    ROW_NUMBER() OVER (
                      PARTITION BY le.ORDEM_CONFECCAO
                      ORDER BY le.SEQ_OPERACAO, le.ROWID
                    ) SEQ
                  , le.SEQUENCIA_ESTAGIO
                  , le.SEQ_OPERACAO
                  , le.ROWID RID
                  FROM pcpc_040 le
                  WHERE le.PERIODO_PRODUCAO = %s
                    AND le.ORDEM_CONFECCAO = %s
                  ORDER BY
                    le.SEQ_OPERACAO
                  , le.ROWID
                ) s
                WHERE s.SEQ <> s.SEQUENCIA_ESTAGIO
            '''
            for lote in lotes:
                # self.stdout.write(str([lote['periodo'], lote['oc']]))
                cursor.execute(sql_seq, [lote['periodo'], lote['oc']])
                seqs = rows_to_dict_list_lower(cursor)
                # self.stdout.write('len(seqs) = {}'.format(len(seqs)))
                # pprint(seqs)
                if len(seqs) == 0:
                    continue
                self.stdout.write(str(lote))

                sql_setseq = '''
                    UPDATE pcpc_040 le
                    SET
                      le.SEQUENCIA_ESTAGIO = %s
                    WHERE le.ROWID = %s
                '''
                for seq in seqs:
                    self.stdout.write(str([seq['rid'], seq['seq']]))
                    # self.stdout.write(str(seq))
                    cursor.execute(sql_setseq, [seq['seq'], seq['rid']])
                # return

        # except Exception as e:
        #     raise CommandError(
        #         'Error repairing SEQUENCIA_ESTAGIO ({})'.format(e))
