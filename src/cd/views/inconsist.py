from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_conn

from utils.functions.models import rows_to_dict_list_lower

import lotes.models


class Inconsistencias(View):

    def __init__(self):
        self.template_name = 'cd/inconsist.html'
        self.title_name = 'Inconsistências Systêxtil'

    def mount_context(self, cursor, ordem, opini):
        step = 10
        data_size = 20
        context = {
            'data_size': data_size,
            'opini': opini,
            'ordem': ordem,
        }

        data = []
        for i in range(0, 999999999, step):
            ops = lotes.models.Lote.objects
            if ordem == 'A':
                ops = ops.filter(
                        op__gt=opini
                    )
            else:
                if opini == -1:
                    ops = ops.filter(
                            op__lte=999999999
                        )
                else:
                    ops = ops.filter(
                            op__lt=opini
                        )
            ops = ops.exclude(
                    local__isnull=True
                ).exclude(
                    local__exact=''
                ).values('op').distinct()
            if ordem == 'A':
                ops = ops.order_by('op')
            else:  # if ordem == 'D':
                ops = ops.order_by('-op')
            ops = ops[i:i+step]
            if len(ops) == 0:
                break

            filtro = ''
            filtro_sep = ''
            for op in ops:
                lotes_recs = lotes.models.Lote.objects.filter(
                        op=op['op']
                    ).exclude(
                        local__isnull=True
                    ).exclude(
                        local__exact='').values('lote').distinct()

                ocs = ''
                sep = ''
                for lote in lotes_recs:
                    ocs += sep + lote['lote'][4:].lstrip('0')
                    sep = ','

                op_ocs = '( op.ORDEM_PRODUCAO = {} ' \
                    'AND le63.ORDEM_CONFECCAO in ({}) )'.format(op['op'], ocs)
                op['oc'] = op_ocs

                filtro += filtro_sep + op_ocs
                filtro_sep = ' OR '

            sql = '''
                SELECT
                  op.ORDEM_PRODUCAO OP
                , op.SITUACAO
                , le.SEQUENCIA_ESTAGIO SEQ
                , le.CODIGO_ESTAGIO EST
                , le63.SEQUENCIA_ESTAGIO SEQ63
                -- , sum(le.QTDE_EM_PRODUCAO_PACOTE) QTD
                , sum(le.QTDE_DISPONIVEL_BAIXA + le.QTDE_CONSERTO) QTD
                FROM PCPC_020 op -- OP capa
                LEFT JOIN PCPC_040 le63 -- lote estágio 63
                  ON le63.ordem_producao = op.ORDEM_PRODUCAO
                 AND le63.CODIGO_ESTAGIO = 63
                LEFT JOIN PCPC_040 le -- lote estágio atual
                  ON le.ordem_producao = op.ORDEM_PRODUCAO
                 AND le.PERIODO_PRODUCAO = le63.PERIODO_PRODUCAO
                 AND le.ORDEM_CONFECCAO = le63.ORDEM_CONFECCAO
                 -- AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
                 AND le.QTDE_PECAS_PROG IS NOT NULL
                 AND le.QTDE_PECAS_PROG <> 0
                 AND (le.QTDE_DISPONIVEL_BAIXA + le.QTDE_CONSERTO) <> 0
                WHERE 1=1
                  -- AND op.SITUACAO <> 9 -- op.COD_CANCELAMENTO = 0
                  AND ({filtro})
                GROUP BY
                  op.ORDEM_PRODUCAO
                , op.SITUACAO
                , le.SEQUENCIA_ESTAGIO
                , le.CODIGO_ESTAGIO
                , le63.SEQUENCIA_ESTAGIO
                ORDER BY
                  op.ORDEM_PRODUCAO
                , le.SEQUENCIA_ESTAGIO
            '''.format(filtro=filtro)
            cursor.execute(sql)
            estagios = rows_to_dict_list_lower(cursor)

            for op in ops:
                row = {}
                sep = ''
                row['op'] = op['op']
                row['op|LINK'] = reverse(
                    'cd:inconsist_detalhe_op', args=[op['op']])
                row['op|TARGET'] = '_blank'
                row['cr'] = ''
                estagios_op = [r for r in estagios if r['op'] == op['op']]
                if len(estagios_op) == 0:
                    row['cr'] = 'OP sem estágio 63'
                else:
                    for estagio_op in estagios_op:
                        if estagio_op['situacao'] == 9:
                            row['cr'] += sep + 'OP Cancelada'
                        elif estagio_op['est'] is None:
                            row['cr'] += sep + 'Finalizados'
                        elif estagio_op['est'] == 63:
                            row['cr'] += sep + 'OK no 63'
                        else:
                            if estagio_op['seq'] < estagio_op['seq63']:
                                row['cr'] += sep + 'Atrasados no {}'.format(
                                    estagio_op['est'])
                            else:
                                row['cr'] += sep + 'Adiantados no {}'.format(
                                    estagio_op['est'])
                        sep = ', '
                if row['cr'] != 'OK no 63':
                    data.append(row)
            if len(data) >= data_size:
                break

        if len(data) >= data_size:
            context.update({'opnext': data[data_size-1]['op']})
        context.update({
            'headers': ['OP', 'Crítica dos lotes'],
            'fields': ['op', 'cr'],
            'data': data[:data_size],
        })
        return context

    def get(self, request, *args, **kwargs):
        if 'opini' in kwargs:
            opini = int(kwargs['opini'])
        else:
            opini = -1

        if 'ordem' in kwargs:
            ordem = kwargs['ordem']
        else:
            ordem = 'A'
        if len(ordem) == 2:
            if ordem[1] == '-':
                if ordem[0] == 'A':
                    ordem = 'D'
                else:
                    ordem = 'A'

        context = {'titulo': self.title_name}
        cursor = db_conn('so', request).cursor()
        data = self.mount_context(cursor, ordem, opini)
        context.update(data)
        return render(request, self.template_name, context)
