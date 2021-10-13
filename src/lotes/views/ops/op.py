from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from geral.functions import config_get_value
from utils.classes import Perf

import lotes.forms as forms
import lotes.queries.lote
import lotes.queries.op
import lotes.queries.os


class Op(View):
    Form_class = forms.OpForm
    template_name = 'lotes/op.html'
    title_name = 'OP'

    def mount_context(self, cursor, op, request):
        p = Perf(False)

        context = {'op': op}

        # informações gerais
        i_data = lotes.queries.op.op_inform(cursor, op, cached=False)
        p.prt('op_inform')

        if len(i_data) == 0:
            context.update({
                'msg_erro': 'OP não encontrada',
            })
        else:

            # Lotes ordenados por OS + referência + estágio
            data = lotes.queries.lote.op_lotes(cursor, op)
            p.prt('op_lotes')

            link = ('LOTE')
            for row in data:
                row['LOTE'] = '{}{:05}'.format(row['PERIODO'], row['OC'])
                row['LINK'] = '/lotes/posicao/{}'.format(row['LOTE'])
            context.update({
                'headers': ('Estágio', 'OS', 'Referência', 'Cor', 'Tamanho',
                            'Período', 'OC', 'Quant.', 'Lote/OC'),
                'fields': ('EST', 'OS', 'REF', 'COR', 'TAM',
                           'PERIODO', 'OC', 'QTD', 'LOTE'),
                'data': data,
                'link': link,
            })

            i2_data = [i_data[0]]
            i3_data = [i_data[0]]
            i4_data = [i_data[0]]

            for row in i_data:
                if row['PEDIDO'] == 0:
                    row['PEDIDO'] = ''
                else:
                    row['PEDIDO|LINK'] = reverse(
                        'producao:pedido__get', args=[row['PEDIDO']])
            val_parm = config_get_value('OP-UNIDADE', request.user)
            if val_parm is None:
                val_parm = 'S'
            context.update({
                'op_unidade': val_parm,
            })

            if val_parm == 'S':
                i_headers = (
                    'Situação', 'Cancelamento', 'Unidade', 'Pedido',
                    'Pedido do cliente', 'Relacionamento com OPs',
                    'Prioridade')
                i_fields = (
                    'SITUACAO', 'CANCELAMENTO', 'UNIDADE', 'PEDIDO',
                    'PED_CLIENTE', 'TIPO_OP',
                    'PRIORIDADE')
            else:
                i_headers = (
                    'Situação', 'Cancelamento', 'Pedido',
                    'Pedido do cliente', 'Relacionamento com OPs',
                    'Prioridade')
                i_fields = (
                    'SITUACAO', 'CANCELAMENTO', 'PEDIDO',
                    'PED_CLIENTE', 'TIPO_OP',
                    'PRIORIDADE')
            context.update({
                'i_headers': i_headers,
                'i_fields': i_fields,
                'i_data': i_data,
            })

            row = i2_data[0]
            row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])
            row['MODELO|LINK'] = reverse(
                'produto:modelo__get', args=[row['MODELO']])
            qtd_lotes_fim = row['LOTES']
            context.update({
                'i2_headers': ('Modelo', 'Tipo', 'Referência',
                               'Alternativa', 'Roteiro',
                               'Descrição', 'Modelagem',
                               'Qtd. Lotes', 'Quant. Itens', 'OS'),
                'i2_fields': ('MODELO', 'TIPO_REF', 'REF',
                              'ALTERNATIVA', 'ROTEIRO',
                              'DESCR_REF', 'MOLDE',
                              'LOTES', 'QTD', 'TEM_OS'),
                'i2_data': i2_data,
            })

            row = i3_data[0]
            row['DT_DIGITACAO'] = row['DT_DIGITACAO'].date()
            if row['DT_CORTE'] is None:
                row['DT_CORTE'] = ''
            else:
                row['DT_CORTE'] = row['DT_CORTE'].date()
            row['PERIODO_INI'] = row['PERIODO_INI'].date()
            row['PERIODO_FIM'] = row['PERIODO_FIM'].date()
            context.update({
                'i3_headers': ('Depósito', 'Período', 'Período Início',
                               'Período Fim', 'Data Digitação', 'Data Corte'),
                'i3_fields': ('DEPOSITO', 'PERIODO', 'PERIODO_INI',
                              'PERIODO_FIM', 'DT_DIGITACAO', 'DT_CORTE'),
                'i3_data': i3_data,
            })

            row = i4_data[0]
            if row['OBSERVACAO'] or row['OBSERVACAO2']:
                if row['OBSERVACAO'] is None:
                    row['OBSERVACAO'] = ''
                if row['OBSERVACAO2'] is None:
                    row['OBSERVACAO2'] = ''
                context.update({
                    'i4_headers': ('Observação', 'Observação 2'),
                    'i4_fields': ('OBSERVACAO', 'OBSERVACAO2'),
                    'i4_data': i4_data,
                })

            # posição de OP
            p_data = lotes.queries.op.posicao_op(cursor, op)
            p.prt('posicao_op')
            if len(p_data) != 0:
                context.update({
                    'p_headers': ('Posição', 'Quantidade', 'Estágio'),
                    'p_fields': ('TIPO', 'QTD', 'ESTAGIO'),
                    'p_style': {2: 'font-weight: bold; text-align: right;'},
                    'p_data': p_data,
                })

            # relacionamentos entre OPs
            r_data = lotes.queries.op.op_relacionamentos(cursor, op)
            p.prt('op_relacionamentos')

            for row in r_data:
                row['OP_REL|LINK'] = '/lotes/op/{}'.format(row['OP_REL'])
                if row['CANC'] == 0:
                    row['CANC'] = 'Ativa'
                else:
                    row['CANC'] = 'Cancelada'
            if len(r_data) != 0:
                context.update({
                    'r_headers': ('OP', 'Tipo de relacionamento',
                                  'OP relacionada', 'Situação'),
                    'r_fields': ('OP', 'REL', 'OP_REL', 'CANC'),
                    'r_data': r_data,
                })

            # Grade
            g_header, g_fields, g_data, _ = lotes.queries.op.op_grade(
                cursor, op=op)
            p.prt('op_sortimento 1ª')

            if len(g_data) != 0:
                context.update({
                    'g_headers': g_header,
                    'g_fields': g_fields,
                    'g_data': g_data,
                })

            # Grade de perda
            gp_header, gp_fields, gp_data, total = \
                lotes.queries.op.op_sortimentos(
                    cursor, op=op, tipo='p', descr_sort=False)
            p.prt('op_sortimentos perda')

            if total != 0:
                context.update({
                    'gp_headers': gp_header,
                    'gp_fields': gp_fields,
                    'gp_data': gp_data,
                })

            # Grade de segunda qualidade
            gs_header, gs_fields, gs_data, total = lotes.queries.op.op_grade(
                cursor, op=op, tipo='s', descr_sort=False
            )
            p.prt('op_sortimentos 2ª')

            if total != 0:
                context.update({
                    'gs_headers': gs_header,
                    'gs_fields': gs_fields,
                    'gs_data': gs_data,
                })

            # Grade de conserto
            gc_header, gc_fields, gc_data, total = \
                lotes.queries.op.op_sortimentos(
                    cursor, op=op, tipo='c', descr_sort=False)
            p.prt('op_sortimentos conserto')

            if total != 0:
                context.update({
                    'gc_headers': gc_header,
                    'gc_fields': gc_fields,
                    'gc_data': gc_data,
                })

            if i_data[0]['TEM_OS'] == 'S':
                # Grade de sem OS
                so_header, so_fields, so_data, total = lotes.queries.op.op_grade(
                    cursor, op=op, tipo='so', descr_sort=False)
                p.prt('op_grade sem_os')

                if total != 0:
                    context.update({
                        'so_headers': so_header,
                        'so_fields': so_fields,
                        'so_data': so_data,
                    })

            # Estágios
            e_data = lotes.queries.op.op_estagios(cursor, op)
            p.prt('op_estagios')

            tem_63 = False
            for row in e_data:
                qtd_lotes_fim -= row['LOTES']
                tem_63 = tem_63 or row['COD_EST'] == 63

            headers_63 = []
            fields_63 = []
            if tem_63:
                headers_63 = ['Itens Endereçados', 'Itens Livres']
                fields_63 = ['ENDERECADO', 'DESENDERECADO']

            context.update({
                'e_headers': [
                    'Estágio', '% Produzido',
                    'Itens 1ª Qualidade', 'Itens 2ª Qualidade',
                    'Itens Perda', 'Itens Conserto'
                ] + headers_63 + [
                    'Itens Em Produção', 'Lotes no estágio',
                    'Seq. Operação', 'Seq. Estágio', 'Est. Anterior',
                ],
                'e_fields': [
                    'EST', 'PERC',
                    'PROD', 'Q2',
                    'PERDA', 'CONSERTO',
                ] + fields_63 + [
                    'EMPROD', 'LOTES',
                    'SEQ_OPER', 'SEQ_EST', 'EST_ANT',
                ],
                'e_data': e_data,
                'qtd_lotes_fim': qtd_lotes_fim,
            })

            # Totais por referência + estágio
            t_data = lotes.queries.op.op_ref_estagio(cursor, op)
            p.prt('op_ref_estagio')

            context.update({
                't_headers': ('Referência', 'Tamanho', 'Cor', 'Estágio',
                              'Qtd. Lotes', 'Quant. Itens'),
                't_fields': ('REF', 'TAM', 'COR', 'EST', 'LOTES', 'QTD'),
                't_data': t_data,
            })

            # OSs da OP
            os_data = lotes.queries.os.op_get_os(cursor, op)
            p.prt('op_get_os')

            if len(os_data) != 0:
                os_link = ('OS')
                for row in os_data:
                    row['LINK'] = '/lotes/os/{}'.format(row['OS'])
                    cnpj = '{:08d}/{:04d}-{:02d}'.format(
                        row['CNPJ9'],
                        row['CNPJ4'],
                        row['CNPJ2'])
                    row['TERC'] = '{} - {}'.format(cnpj, row['NOME'])
                context.update({
                    'os_headers': ('OS', 'Serviço', 'Terceiro',
                                   'Emissão', 'Entrega',
                                   'Situação', 'Cancelamento',
                                   'Lotes', 'Quant.'),
                    'os_fields': ('OS', 'SERV', 'TERC',
                                  'DATA_EMISSAO', 'DATA_ENTREGA',
                                  'SITUACAO', 'CANC',
                                  'LOTES', 'QTD'),
                    'os_data': os_data,
                    'os_link': os_link,
                })

            if i_data[0]['TEM_OS'] == 'S':
                # Totais por OS + referência
                o_data = lotes.queries.op.op_os_ref(cursor, op)
                p.prt('op_os_ref')

                o_link = ('OS')
                for row in o_data:
                    if row['OS']:
                        row['LINK'] = '/lotes/os/{}'.format(row['OS'])
                    else:
                        row['LINK'] = None
                context.update({
                    'o_headers': ('OS', 'Referência', 'Tamanho', 'Cor',
                                'Qtd. Lotes', 'Quant. Itens'),
                    'o_fields': ('OS', 'REF', 'TAM', 'COR', 'LOTES', 'QTD'),
                    'o_data': o_data,
                    'o_link': o_link,
                })

            # Detalhamento de movimentações de estágios
            u_data = lotes.queries.op.op_movi_estagios(cursor, op)
            p.prt('op_movi_estagios')

            for row in u_data:
                if row['DT_MIN'] == row['DT_MAX']:
                    row['DT_MAX'] = '='
                else:
                    row['DT_MAX'] = row['DT_MAX'].date()
                row['DT_MIN'] = row['DT_MIN'].date()
            context.update({
                'u_headers': ('Estagio', 'Movimento', 'De', 'Até',
                              'Usuário', 'Lotes'),
                'u_fields': ('EST', 'MOV', 'DT_MIN', 'DT_MAX',
                             'USU', 'LOTES'),
                'u_data': u_data,
            })
        return context

    def get(self, request, *args, **kwargs):
        if 'op' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'op' in kwargs:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, op, request))
        context['form'] = form
        return render(request, self.template_name, context)
