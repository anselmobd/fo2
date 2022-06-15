import datetime
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from fo2.connections import db_cursor_so

import logistica.models as models
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


class Command(BaseCommand):
    help = 'Repair zeroed SEQUENCIA_ESTAGIO field in PCPC_040 TABLE.'

    def handle(self, *args, **options):
        self.stdout.write('---\n{}'.format(datetime.datetime.now()))
        try:
            cursor = db_cursor_so()

            # get lotes com SEQUENCIA_ESTAGIO zerado e mais de um estágio
            sql_get = '''
                SELECT
                    r.PERIODO_PRODUCAO PERIODO
                  , r.ORDEM_CONFECCAO OC
                FROM (
                  SELECT DISTINCT
                    le.PERIODO_PRODUCAO
                  , le.ORDEM_CONFECCAO
                  FROM pcpc_040 le
                  WHERE le.SEQUENCIA_ESTAGIO = 0
                  ORDER BY
                    le.PERIODO_PRODUCAO
                  , le.ORDEM_CONFECCAO
                ) r
                WHERE rownum <= 100
            '''
            debug_cursor_execute(cursor, sql_get)
            lotes = dictlist_lower(cursor)
            # self.stdout.write('len(lotes) = {}'.format(len(lotes)))
            # pprint(lotes)

            # get new value to SEQUENCIA_ESTAGIO and ROWIDs
            sql_seq = '''
                SELECT
                  ROW_NUMBER() OVER (
                    PARTITION BY le.ORDEM_CONFECCAO
                    ORDER BY le.SEQ_OPERACAO, le.ROWID
                  ) SEQ
                , le.ROWID RID
                FROM pcpc_040 le
                WHERE le.PERIODO_PRODUCAO = %s
                  AND le.ORDEM_CONFECCAO = %s
                ORDER BY
                  le.SEQ_OPERACAO
            '''
            for lote in lotes:
                # self.stdout.write(str([lote['periodo'], lote['oc']]))
                self.stdout.write(str(lote))
                debug_cursor_execute(cursor, sql_seq, [lote['periodo'], lote['oc']])
                seqs = dictlist_lower(cursor)
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
                    debug_cursor_execute(cursor, sql_setseq, [seq['seq'], seq['rid']])

        except Exception as e:
            raise CommandError(
                'Error repairing SEQUENCIA_ESTAGIO ({})'.format(e))
