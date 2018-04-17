import sys

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import F, Sum
from django.utils import timezone

from fo2.models import rows_to_dict_list_lower
import lotes.models as models


class Command(BaseCommand):
    help = 'Syncronizing Lotes'
    __MAX_TASKS__ = 10

    def itercur(self, cursor):
        for row in cursor:
            yield row

    def get_lotes_op(self, op):
        cursor = connections['so'].cursor()
        sql = '''
            SELECT DISTINCT
              le.ORDEM_PRODUCAO OP
            , le.PERIODO_PRODUCAO PERIODO
            , le.ORDEM_CONFECCAO OC
            , le.PROCONF_GRUPO REF
            , le.PROCONF_SUBGRUPO TAM
            , t.ORDEM_TAMANHO ORD_TAM
            , le.PROCONF_ITEM COR
            , le.QTDE_PECAS_PROG QUANT
            FROM PCPC_040 le -- lote estágio
            LEFT JOIN BASI_220 t
              ON t.TAMANHO_REF = le.PROCONF_SUBGRUPO
            WHERE le.ORDEM_PRODUCAO = %s
            ORDER BY
              le.ORDEM_PRODUCAO
            , le.ORDEM_CONFECCAO
        '''
        cursor.execute(sql, [op])
        return rows_to_dict_list_lower(cursor)

    def set_lote(self, lote, row):
        lote.lote = row['lote']
        lote.op = row['op']
        lote.referencia = row['ref']
        lote.tamanho = row['tam']
        lote.ordem_tamanho = row['ord_tam']
        lote.cor = row['cor']
        lote.qtd_produzir = row['quant']

    def inclui(self, op):
        self.stdout.write(
            'Incluindo lotes da OP {}'.format(op))
        lotes = self.get_lotes_op(op)
        for row in lotes:
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            lote = models.Lote()
            self.set_lote(lote, row)
            lote.save()

    def atualiza(self, op):
        self.stdout.write(
            'Atualizando lotes da OP {}'.format(op))
        lotes = self.get_lotes_op(op)
        for row in lotes:
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            try:
                lote = models.Lote.objects.get(lote=row['lote'])
            except models.Lote.DoesNotExist:
                lote = None
            if not lote:
                lote = models.Lote()
            self.set_lote(lote, row)
            lote.save()

    def handle(self, *args, **options):
        try:

            # pega no Systêxtil a lista OPs com um valor de teste de quantidade
            cursor_s = connections['so'].cursor()
            sql = '''
                WITH lotes AS
                (
                  SELECT DISTINCT
                    le.ORDEM_PRODUCAO
                  , le.ORDEM_CONFECCAO
                  , le.QTDE_PECAS_PROG
                  FROM PCPC_040 le -- lote estágio
                  JOIN PCPC_020 op -- OP capa
                    ON op.ordem_producao = le.ORDEM_PRODUCAO
                  WHERE op.COD_CANCELAMENTO = 0
                    --AND op.ORDEM_PRODUCAO < 80
                  ORDER BY
                    le.ORDEM_PRODUCAO
                  , le.ORDEM_CONFECCAO
                )
                SELECT
                  lo.ORDEM_PRODUCAO op
                , sum(lo.QTDE_PECAS_PROG*(1+mod(lo.ORDEM_CONFECCAO, 10))) prog
                FROM lotes lo
                GROUP BY
                  lo.ORDEM_PRODUCAO
                ORDER BY
                  1
            '''
            cursor_s.execute(sql)
            fidx_s = {
                item[0].lower(): i
                for i, item in enumerate(cursor_s.description)}

            # pega no Fo2 a lista OPs com um valor de teste de quantidade
            cursor_f = connections['default'].cursor()
            sql = '''
                SELECT
                  le.op
                , sum(le.qtd_produzir*(1+substr(le.lote, 9, 1))) prog
                FROM fo2_cd_lote le
                --WHERE le.OP < 20
                GROUP BY
                  le.op
                ORDER BY
                  1
            '''
            cursor_f.execute(sql)
            fidx_f = {
                item[0].lower(): i
                for i, item in enumerate(cursor_f.description)}

            ics = self.itercur(cursor_s)
            icf = self.itercur(cursor_f)

            op_s = -1
            op_f = -1
            inclui_op = []
            atualiza_op = []
            count_task = 0
            while count_task < self.__MAX_TASKS__:

                if op_s != sys.maxsize and (op_s < 0 or op_s <= op_f):
                    try:
                        row_s = next(ics)
                        getop_s = row_s[fidx_f['op']]
                    except StopIteration:
                        getop_s = sys.maxsize

                if op_f != sys.maxsize and (op_f < 0 or op_f <= op_s):
                    try:
                        row_f = next(icf)
                        getop_f = row_f[fidx_f['op']]
                    except StopIteration:
                        getop_f = sys.maxsize

                op_s = getop_s
                op_f = getop_f

                if op_s == sys.maxsize and op_f == sys.maxsize:
                    break

                if op_s < op_f:
                    self.stdout.write(
                        'Incluir OP {} no Fo2'.format(op_s))
                    inclui_op.append(op_s)
                    count_task += 1
                elif op_s > op_f:
                    self.stdout.write(
                        'OP {} não mais ativa'.format(op_f))
                else:
                    if row_s[fidx_s['prog']] != row_f[fidx_f['prog']]:
                        self.stdout.write(
                            'Atualizar OP {} no Fo2'.format(op_f))
                        atualiza_op.append(op_s)
                        count_task += 1

            if len(inclui_op) != 0:
                for op in inclui_op:
                    self.inclui(op)

            if len(atualiza_op) != 0:
                for op in atualiza_op:
                    self.atualiza(op)

        except Exception as e:
            raise CommandError('Error syncing lotes "{}"'.format(e))
