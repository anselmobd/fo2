import copy

from django.shortcuts import render
from django.db import connections
from django.urls import reverse
from django.views import View

from fo2.template import group_rowspan

from lotes.forms import OpForm
import lotes.models as models


class Op(View):
    Form_class = OpForm
    template_name = 'lotes/op.html'
    title_name = 'OP'

    def mount_context(self, cursor, op):
        context = {'op': op}

        # Lotes ordenados por OS + referência + estágio
        data = models.op_lotes(cursor, op)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Lotes não encontrados',
            })
        else:
            link = ('LOTE')
            for row in data:
                row['LOTE'] = '{}{:05}'.format(row['PERIODO'], row['OC'])
                row['LINK'] = '/lotes/posicao/{}'.format(row['LOTE'])
            context.update({
                'headers': ('Estágio', 'OS', 'Referência', 'Cor', 'Tamanho',
                            'Período', 'OC', 'Quant.', 'Lote'),
                'fields': ('EST', 'OS', 'REF', 'COR', 'TAM',
                           'PERIODO', 'OC', 'QTD', 'LOTE'),
                'data': data,
                'link': link,
            })

            # informações gerais
            i_data = models.op_inform(cursor, op)
            i2_data = [i_data[0]]
            i3_data = [i_data[0]]
            i4_data = [i_data[0]]

            for row in i_data:
                if row['OP_REL'] == 0:
                    row['OP_REL'] = ''
                else:
                    row['OP_REL|LINK'] = '/lotes/op/{}'.format(row['OP_REL'])
                if row['PEDIDO'] == 0:
                    row['PEDIDO'] = ''
                else:
                    row['PEDIDO|LINK'] = '/lotes/pedido/{}'.format(
                        row['PEDIDO'])
            i_group = ['SITUACAO', 'CANCELAMENTO', 'PEDIDO', 'PED_CLIENTE']
            group_rowspan(i_data, i_group)
            context.update({
                'i_headers': ('Situação', 'Cancelamento', 'Unidade', 'Pedido',
                              'Pedido do cliente', 'Tipo de OP',
                              'OP relacionada'),
                'i_fields': ('SITUACAO', 'CANCELAMENTO', 'UNIDADE', 'PEDIDO',
                             'PED_CLIENTE', 'TIPO_OP', 'OP_REL'),
                'i_group': i_group,
                'i_data': i_data,
            })

            row = i2_data[0]
            row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])
            row['MODELO|LINK'] = reverse(
                'produto:modelo__get', args=[row['MODELO']])
            qtd_lotes_fim = row['LOTES']
            context.update({
                'i2_headers': ('Modelo', 'Tipo de referência', 'Referência',
                               'Alternativa', 'Roteiro',
                               'Descrição', 'Modelagem',
                               'Qtd. Lotes', 'Quant. Itens'),
                'i2_fields': ('MODELO', 'TIPO_REF', 'REF',
                              'ALTERNATIVA', 'ROTEIRO',
                              'DESCR_REF', 'MOLDE',
                              'LOTES', 'QTD'),
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

            # Grade
            g_header, g_fields, g_data = models.op_sortimento(cursor, op)
            if len(g_data) != 0:
                context.update({
                    'g_headers': g_header,
                    'g_fields': g_fields,
                    'g_data': g_data,
                })

            # Grade de perda
            gp_header, gp_fields, gp_data, total = models.op_sortimentos(
                cursor, op, 'p')
            if total != 0:
                context.update({
                    'gp_headers': gp_header,
                    'gp_fields': gp_fields,
                    'gp_data': gp_data,
                })

            # Grade de segunda qualidade
            gs_header, gs_fields, gs_data, total = models.op_sortimentos(
                cursor, op, 's')
            if total != 0:
                context.update({
                    'gs_headers': gs_header,
                    'gs_fields': gs_fields,
                    'gs_data': gs_data,
                })

            # Grade de conserto
            gc_header, gc_fields, gc_data, total = models.op_sortimentos(
                cursor, op, 'c')
            if total != 0:
                context.update({
                    'gc_headers': gc_header,
                    'gc_fields': gc_fields,
                    'gc_data': gc_data,
                })

            # Estágios
            e_data = models.op_estagios(cursor, op)
            for row in e_data:
                qtd_lotes_fim -= row['LOTES']
            context.update({
                'e_headers': ('Estágio', '% Produzido',
                              'Itens 1ª Qualidade', 'Itens 2ª Qualidade',
                              'Itens Perda', 'Itens Conserto',
                              'Lotes no estágio'),
                'e_fields': ('EST', 'PERC',
                             'PROD', 'Q2',
                             'PERDA', 'CONSERTO', 'LOTES'),
                'e_data': e_data,
                'qtd_lotes_fim': qtd_lotes_fim,
            })

            # Totais por referência + estágio
            t_data = models.op_ref_estagio(cursor, op)
            context.update({
                't_headers': ('Referência', 'Tamanho', 'Cor', 'Estágio',
                              'Qtd. Lotes', 'Quant. Itens'),
                't_fields': ('REF', 'TAM', 'COR', 'EST', 'LOTES', 'QTD'),
                't_data': t_data,
            })

            # OSs da OP
            os_data = models.op_get_os(cursor, op)
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

            # Totais por OS + referência
            o_data = models.op_os_ref(cursor, op)
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
            u_data = models.op_movi_estagios(cursor, op)
            for row in u_data:
                if row['DT_MIN'] == row['DT_MAX']:
                    row['DT_MAX'] = '='
                else:
                    row['DT_MAX'] = row['DT_MAX'].date()
                row['DT_MIN'] = row['DT_MIN'].date()
            context.update({
                'u_headers': ('Estagio', 'De', 'Até',
                              'Usuário', 'Lotes'),
                'u_fields': ('EST', 'DT_MIN', 'DT_MAX',
                             'USUARIO_SYSTEXTIL', 'LOTES'),
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
        if 'op' in kwargs:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)
