import sys
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from fo2.models import rows_to_dict_list_lower
import lotes.models as models


class Command(BaseCommand):
    help = 'Syncronizing Lotes'
    __MAX_TASKS = 10

    def iter_cursor(self, cursor):
        columns = [i[0].lower() for i in cursor.description]
        for row in cursor:
            dict_row = dict(zip(columns, row))
            yield dict_row

    def get_ops_trail_s(self):
        cursor_s = connections['so'].cursor()
        sql = '''
            SELECT
              lo.ORDEM_PRODUCAO op
            , sum(
                ( 1
                + lo.QTDE_PECAS_PROG
                + lo.QTDE_EM_PRODUCAO_PACOTE
                + lo.QTDE_PECAS_PROD
                )
              * (1 + lo.CODIGO_ESTAGIO)
              * (1 + mod(lo.ORDEM_CONFECCAO, 111))
              ) trail
            FROM PCPC_040 lo -- lote estágio
            JOIN PCPC_020 op -- OP capa
              ON op.ordem_producao = lo.ORDEM_PRODUCAO
            WHERE op.COD_CANCELAMENTO = 0
            GROUP BY
              lo.ORDEM_PRODUCAO
            ORDER BY
              lo.ORDEM_PRODUCAO
        '''
        cursor_s.execute(sql)
        return self.iter_cursor(cursor_s)

    def get_ops_trail_f(self):
        cursor_f = connections['default'].cursor()
        sql = '''
            SELECT
              le.op
            , sum( le.trail ) trail
            FROM fo2_cd_lote le
            GROUP BY
              le.op
            ORDER BY
              le.op
        '''
        cursor_f.execute(sql)
        return self.iter_cursor(cursor_f)

    def get_lotes_op(self, op):
        cursor = connections['so'].cursor()
        sql = '''
            SELECT
              lote.OP
            , lote.PERIODO
            , lote.OC
            , lote.REF
            , lote.TAM
            , lote.ORD_TAM
            , lote.COR
            , lote.QTD_PRODUZIR
            --, lote.ULTIMO_ESTAGIO
            , lote.TRAIL
            , CASE WHEN l.ORDEM_CONFECCAO IS NULL THEN 999
              ELSE l.CODIGO_ESTAGIO END ESTAGIO
            , CASE WHEN l.ORDEM_CONFECCAO IS NULL THEN lf.QTDE_PECAS_PROD
              ELSE l.QTDE_EM_PRODUCAO_PACOTE END QTD
            FROM
            (
              SELECT
                le.ORDEM_PRODUCAO OP
              , le.PERIODO_PRODUCAO PERIODO
              , le.ORDEM_CONFECCAO OC
              , le.PROCONF_GRUPO REF
              , le.PROCONF_SUBGRUPO TAM
              , t.ORDEM_TAMANHO ORD_TAM
              , le.PROCONF_ITEM COR
              , le.QTDE_PECAS_PROG QTD_PRODUZIR
              , max(le.CODIGO_ESTAGIO) ULTIMO_ESTAGIO
              , max(le.SEQUENCIA_ESTAGIO) ULTIMA_SEQ_ESTAGIO
              , sum(
                  ( 1
                  + le.QTDE_PECAS_PROG
                  + le.QTDE_EM_PRODUCAO_PACOTE
                  + le.QTDE_PECAS_PROD
                  )
                * (1 + le.CODIGO_ESTAGIO)
                * (1 + mod(le.ORDEM_CONFECCAO, 111))
                ) trail
              FROM PCPC_040 le -- lote estágio
              LEFT JOIN BASI_220 t
                ON t.TAMANHO_REF = le.PROCONF_SUBGRUPO
              WHERE le.ORDEM_PRODUCAO = %s
            --    AND le.ORDEM_CONFECCAO = 22
                AND le.QTDE_PECAS_PROG IS NOT NULL
                AND le.QTDE_PECAS_PROG <> 0
              GROUP BY
                le.ORDEM_PRODUCAO
              , le.PERIODO_PRODUCAO
              , le.ORDEM_CONFECCAO
              , le.PROCONF_GRUPO
              , le.PROCONF_SUBGRUPO
              , t.ORDEM_TAMANHO
              , le.PROCONF_ITEM
              , le.QTDE_PECAS_PROG
              ORDER BY
                le.ORDEM_PRODUCAO
              , le.ORDEM_CONFECCAO
            ) lote
            LEFT JOIN PCPC_040 l -- lote estágio
              ON l.ORDEM_PRODUCAO = lote.OP
             AND l.ORDEM_CONFECCAO = lote.OC
             AND l.QTDE_EM_PRODUCAO_PACOTE <> 0
            LEFT JOIN PCPC_040 lf -- lote estágio
              ON l.ORDEM_CONFECCAO IS NULL
             AND lf.ORDEM_PRODUCAO = lote.OP
             AND lf.ORDEM_CONFECCAO = lote.OC
             AND (  (   lote.ULTIMA_SEQ_ESTAGIO = 0
                    AND lf.CODIGO_ESTAGIO = lote.ULTIMO_ESTAGIO)
                 OR (   lote.ULTIMA_SEQ_ESTAGIO <> 0
                    AND lf.SEQUENCIA_ESTAGIO = lote.ULTIMA_SEQ_ESTAGIO)
                 )
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
        if lote.estagio != row['estagio']:
            alter = True
            lote.estagio = row['estagio']
            # self.stdout.write('estagio {}'.format(lote.estagio))
        if lote.qtd != row['qtd']:
            alter = True
            lote.qtd = row['qtd']
            # self.stdout.write('qtd {}'.format(lote.qtd))
        if lote.qtd_produzir != row['qtd_produzir']:
            alter = True
            lote.qtd_produzir = row['qtd_produzir']
            # self.stdout.write('qtd_produzir {}'.format(lote.qtd_produzir))
        if lote.trail != row['trail']:
            alter = True
            lote.trail = row['trail']
            # self.stdout.write('trail {}'.format(lote.trail))
        return alter

    def inclui(self, op):
        self.stdout.write(
            'Incluindo lotes da OP {}'.format(op))
        lotes = self.get_lotes_op(op)
        self.stdout.write(
            'Sistêxtil tem {} lotes'.format(len(lotes)), ending='')
        for row in lotes:
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            lote = models.Lote()
            self.set_lote(lote, row)
            lote.save()
            self.stdout.write(
                ' {}{}'.format(
                    'I', row['lote'][4:].lstrip('0')), ending='')
        self.stdout.write('')

    def atualiza(self, op):
        self.stdout.write(
            'Atualizando lotes da OP {}'.format(op))

        # atualizando Systêxtil -> Fo2
        lotes = self.get_lotes_op(op)
        self.stdout.write(
            'Sistêxtil tem {} lotes'.format(len(lotes)), ending='')
        sys_lotes = []
        for row in lotes:
            acao = ''
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            sys_lotes.append(row['lote'])
            # self.stdout.write('OC {}'.format(row['oc']))
            try:
                # self.stdout.write('try')
                lote = models.Lote.objects.get(lote=row['lote'])
                acao = 'A'
            except models.Lote.DoesNotExist:
                # self.stdout.write('except')
                lote = None
            if not lote:
                # self.stdout.write('not lote')
                acao = 'I'
                lote = models.Lote()
            if self.set_lote(lote, row):
                # self.stdout.write('save')
                lote.save()
                self.stdout.write(
                    ' {}{}'.format(
                        acao, row['lote'][4:].lstrip('0')), ending='')

        # atualizando Fo2 -> Systêxtil
        lotes = models.Lote.objects.filter(op=op)
        self.stdout.write('')
        self.stdout.write('Fo2 tem {} lotes'.format(len(lotes)), ending='')
        for row in lotes:
            if row.lote not in sys_lotes:
                row.delete()
                self.stdout.write(
                    ' E{}'.format(row.lote[4:].lstrip('0')), ending='')
        self.stdout.write('')

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

    def init_tasks(self):
        self.inclui_op = []
        self.atualiza_op = []
        self.exclui_op = []

    def exec_tasks(self):
        if len(self.inclui_op) != 0:
            for op in self.inclui_op:
                self.inclui(op)

        if len(self.atualiza_op) != 0:
            for op in self.atualiza_op:
                self.atualiza(op)

        if len(self.exclui_op) != 0:
            for op in self.exclui_op:
                self.exclui(op)

    def handle(self, *args, **options):
        self.stdout.write('---\n{}'.format(datetime.datetime.now()))
        try:

            # pega no Systêxtil a lista OPs com um valor de teste de quantidade
            ics = self.get_ops_trail_s()

            # pega no Fo2 a lista OPs com um valor de teste de quantidade
            icf = self.get_ops_trail_f()

            op_s = -1
            op_f = -1
            self.init_tasks()
            count_task = 0
            while count_task < self.__MAX_TASKS:

                if op_s != sys.maxsize and (op_s < 0 or op_s <= op_f):
                    try:
                        row_s = next(ics)
                        getop_s = row_s['op']
                    except StopIteration:
                        getop_s = sys.maxsize

                if op_f != sys.maxsize and (op_f < 0 or op_f <= op_s):
                    try:
                        row_f = next(icf)
                        getop_f = row_f['op']
                    except StopIteration:
                        getop_f = sys.maxsize

                op_s = getop_s
                op_f = getop_f

                if op_s == sys.maxsize and op_f == sys.maxsize:
                    break

                if op_s < op_f:
                    self.stdout.write(
                        'Incluir OP {} no Fo2'.format(op_s))
                    self.inclui_op.append(op_s)
                    count_task += 1
                elif op_s > op_f:
                    self.stdout.write(
                        'OP {} não mais ativa'.format(op_f))
                    self.exclui_op.append(op_f)
                else:
                    if row_s['trail'] != row_f['trail']:
                        self.stdout.write(
                            'Atualizar OP {} no Fo2'.format(op_f))
                        self.atualiza_op.append(op_s)
                        count_task += 1

            self.exec_tasks()

        except Exception as e:
            raise CommandError('Error syncing lotes "{}"'.format(e))
