from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from base.forms.forms2 import PedidoForm2
from geral.functions import get_empresa

import lotes.models as models
import lotes.queries as queries


class Pedido(View):
    Form_class = PedidoForm2
    title_name = 'Pedido'
    template_name = 'lotes/pedido.html'

    def set_context(self, request):
        self.context = {
            'titulo': self.title_name,
        }
        if get_empresa(request) == 'agator':
            self.empresa = 2
            self.context.update({
                'extends_html': 'lotes/index_agator.html',
            })
        else:
            self.empresa = 1
            self.context.update({
                'extends_html': 'lotes/index.html'
            })

    def mount_context(self, cursor, pedido):
        self.context.update({
            'pedido': pedido,
        })

        # informações gerais
        data = queries.pedido.ped_inform(cursor, pedido, empresa=self.empresa)
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Pedido não encontrado',
            })
        else:
            for row in data:
                row['DT_EMISSAO'] = row['DT_EMISSAO'].date()
                row['DT_EMBARQUE'] = row['DT_EMBARQUE'].date()
                if row['OBSERVACAO'] is None:
                    row['OBSERVACAO'] = '-'
            self.context.update({
                'headers': ('Data de emissão', 'Data de embarque',
                            'Cliente', 'Código do pedido no cliente'),
                'fields': ('DT_EMISSAO', 'DT_EMBARQUE',
                           'CLIENTE', 'PEDIDO_CLIENTE'),
                'data': data,
            })
            self.context.update({
                'headers2': ('Status do pedido', 'Situação da venda',
                             'Observação'),
                'fields2': ('STATUS_PEDIDO', 'SITUACAO_VENDA',
                            'OBSERVACAO'),
                'data2': data,
            })

            # Depósitos
            d_data = queries.pedido.ped_dep_qtd(cursor, pedido)
            self.context.update({
                'd_headers': ('Depósito', 'Quantidade'),
                'd_fields': ('DEPOSITO', 'QTD'),
                'd_data': d_data,
            })

            # OPs
            o_data = queries.pedido.ped_op(cursor, pedido)
            for row in o_data:
                row['ORDEM_PRODUCAO|LINK'] = '/lotes/op/{}'.format(
                    row['ORDEM_PRODUCAO'])
                row['REFERENCIA_PECA|LINK'] = reverse(
                    'produto:ref__get', args=[row['REFERENCIA_PECA']])
                if row['ORDEM_PRINCIPAL'] == 0:
                    row['ORDEM_PRINCIPAL'] == ''
                else:
                    row['ORDEM_PRINCIPAL|LINK'] = '/lotes/op/{}'.format(
                        row['ORDEM_PRINCIPAL'])
                row['DT_DIGITACAO'] = row['DT_DIGITACAO'].date()
                if row['DT_CORTE'] is None:
                    row['DT_CORTE'] = '-'
                else:
                    row['DT_CORTE'] = row['DT_CORTE'].date()
                if row['SITUACAO'] == 9:
                    row['SITUACAO'] = 'Cancelada'
                else:
                    row['SITUACAO'] = 'Ativa'
            self.context.update({
                'o_headers': ('Stuação', 'OP', 'Tipo',
                              'Referência', 'OP principal', 'Quantidade',
                              'Data Digitação', 'Data Corte'),
                'o_fields': ('SITUACAO', 'ORDEM_PRODUCAO', 'TIPO',
                             'REFERENCIA_PECA', 'ORDEM_PRINCIPAL', 'QTD',
                             'DT_DIGITACAO', 'DT_CORTE'),
                'o_data': o_data,
            })

            # NFs
            nf_data = queries.pedido.ped_nf(cursor, pedido)
            for row in nf_data:
                row['NF|LINK'] = reverse(
                    'contabil:nota_fiscal__get', args=[row['NF']])
                if row['SITUACAO'] == 1:
                    row['SITUACAO'] = 'Ativa'
                else:
                    row['SITUACAO'] = 'Cancelada'

                if row['NF_DEVOLUCAO'] is None:
                    row['NF_DEVOLUCAO'] = '-'
                else:
                    row['SITUACAO'] += '/Devolvida'

            self.context.update({
                'nf_headers': ('NF', 'Data', 'Situação', 'Valor',
                               'NF Devolução'),
                'nf_fields': ('NF', 'DATA', 'SITUACAO', 'VALOR',
                              'NF_DEVOLUCAO'),
                'nf_data': nf_data,
            })

            # Grade
            g_header, g_fields, g_data, g_style, g_total = \
                queries.pedido.sortimento(cursor, pedido=pedido, total='Total')
            if len(g_data) != 0:
                for i in range(1, len(g_fields)):
                    i_column = i + 1
                    g_style[i_column] = g_style[i_column] + \
                        'border-left-style: solid;' \
                        'border-left-width: thin;' \
                        'text-align: right;'

                self.context.update({
                    'g_headers': g_header,
                    'g_fields': g_fields,
                    'g_data': g_data,
                    'g_style': g_style,
                    'g_total': g_total,
                })


    def get(self, request, *args, **kwargs):
        self.set_context(request)
        if 'pedido' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            form = self.Form_class()
            self.context['form'] = form
            return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.set_context(request)
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'pedido' in kwargs:
            form.data['pedido'] = kwargs['pedido']
        if form.is_valid():
            pedido = form.cleaned_data['pedido']
            cursor = db_cursor_so(request)
            self.mount_context(cursor, pedido)
        self.context['form'] = form
        return render(request, self.template_name, self.context)
