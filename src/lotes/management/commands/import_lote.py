import sys
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import connections

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
              AND le.QTDE_PECAS_PROG IS NOT NULL
              AND le.QTDE_PECAS_PROG <> 0
            ORDER BY
              le.ORDEM_PRODUCAO
            , le.ORDEM_CONFECCAO
        '''
        cursor.execute(sql, [op])
        return rows_to_dict_list_lower(cursor)

    def set_lote(self, lote, row):
        alter = False
        if lote.lote != row['lote']:
            alter = True
            lote.lote = row['lote']
            # self.stdout.write('lote {}'.format(lote.lote))
        if lote.op != row['op']:
            alter = True
            lote.op = row['op']
            # self.stdout.write('op {}'.format(lote.op))
        if lote.referencia != row['ref']:
            alter = True
            lote.referencia = row['ref']
            # self.stdout.write('ref {}'.format(lote.referencia))
        if lote.tamanho != row['tam']:
            alter = True
            lote.tamanho = row['tam']
            # self.stdout.write('tam {}'.format(lote.tamanho))
        if lote.ordem_tamanho != row['ord_tam']:
            alter = True
            lote.ordem_tamanho = row['ord_tam']
            # self.stdout.write('ord_tam {}'.format(lote.ordem_tamanho))
        if lote.cor != row['cor']:
            alter = True
            lote.cor = row['cor']
            # self.stdout.write('cor {}'.format(lote.cor))
        if lote.qtd_produzir != row['quant']:
            alter = True
            lote.qtd_produzir = row['quant']
            # self.stdout.write('quant {}'.format(lote.qtd_produzir))
        return alter

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

        # atualizando Systêxtil -> Fo2
        lotes = self.get_lotes_op(op)
        self.stdout.write('Sistêxtil tem {} lotes'.format(len(lotes)))
        sys_lotes = []
        for row in lotes:
            acao = ''
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            sys_lotes.append(row['lote'])
            # self.stdout.write('OC {}'.format(row['oc']))
            try:
                # self.stdout.write('try')
                lote = models.Lote.objects.get(lote=row['lote'])
                acao = 'alterado'
            except models.Lote.DoesNotExist:
                # self.stdout.write('except')
                lote = None
            if not lote:
                # self.stdout.write('not lote')
                acao = 'incluido'
                lote = models.Lote()
            if self.set_lote(lote, row):
                # self.stdout.write('save')
                lote.save()
                self.stdout.write(
                    'Lote {} {}'.format(row['lote'], acao))

        # atualizando Fo2 -> Systêxtil
        lotes = models.Lote.objects.filter(op=op)
        self.stdout.write('Fo2 tem {} lotes'.format(len(lotes)))
        for row in lotes:
            if row.lote not in sys_lotes:
                row.delete()
                self.stdout.write(
                    'Lote {} excluido'.format(row.lote))

    def exclui(self, op):
        self.stdout.write(
            'Excluindo lotes da OP {}'.format(op))
        lotes = models.Lote.objects.filter(op=op)
        lotes_localizados = lotes.exclude(
                local__isnull=True
            ).exclude(
                local__exact='')
        self.stdout.write('Fo2 tem {} lotes'.format(len(lotes)))
        self.stdout.write('Fo2 tem {} lotes localizados'.format(
            len(lotes_localizados)))
        if len(lotes_localizados) == 0:
            for row in lotes:
                row.delete()
        else:
            self.stdout.write('OP {} não excluida em Fo2'.format(op))

    def handle(self, *args, **options):
        self.stdout.write('---\n{}'.format(datetime.datetime.now()))
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
                    AND le.QTDE_PECAS_PROG IS NOT NULL
                    AND le.QTDE_PECAS_PROG <> 0
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
                , sum( le.qtd_produzir
                       * ( 1
                         + CAST( substr(le.lote, 9, 1) as INTEGER )
                         )
                     ) prog
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
            exclui_op = []
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
                    exclui_op.append(op_f)
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

            if len(exclui_op) != 0:
                for op in exclui_op:
                    self.exclui(op)

        except Exception as e:
            raise CommandError('Error syncing lotes "{}"'.format(e))
