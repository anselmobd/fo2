from pprint import pprint
import copy

from django.shortcuts import render
from django.db import connections
from django.urls import reverse
from django.views import View

from utils.views import totalize_grouped_data
from fo2.template import group_rowspan

import lotes.forms as forms
import lotes.models as models


class Pedido(View):
    Form_class = forms.PedidoForm
    template_name = 'lotes/pedido.html'
    title_name = 'Pedido'

    def mount_context(self, cursor, pedido):
        context = {'pedido': pedido}

        # informações gerais
        data = models.ped_inform(cursor, pedido)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Pedido não encontrado',
            })
        else:
            for row in data:
                row['DT_EMISSAO'] = row['DT_EMISSAO'].date()
                row['DT_EMBARQUE'] = row['DT_EMBARQUE'].date()
                if row['OBSERVACAO'] is None:
                    row['OBSERVACAO'] = '-'
            context.update({
                'headers': ('Data de emissão', 'Data de embarque',
                            'Cliente', 'Código do pedido no cliente'),
                'fields': ('DT_EMISSAO', 'DT_EMBARQUE',
                           'CLIENTE', 'PEDIDO_CLIENTE'),
                'data': data,
            })
            context.update({
                'headers2': ('Status do pedido', 'Situação da venda',
                             'Observação'),
                'fields2': ('STATUS_PEDIDO', 'SITUACAO_VENDA',
                            'OBSERVACAO'),
                'data2': data,
            })

            # Depósitos
            d_data = models.ped_dep_qtd(cursor, pedido)
            context.update({
                'd_headers': ('Depósito', 'Quantidade'),
                'd_fields': ('DEPOSITO', 'QTD'),
                'd_data': d_data,
            })

            # OPs
            o_data = models.ped_op(cursor, pedido)
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
            context.update({
                'o_headers': ('OP', 'Tipo', 'Referência',
                              'OP principal', 'Quantidade',
                              'Data Digitação', 'Data Corte'),
                'o_fields': ('ORDEM_PRODUCAO', 'TIPO', 'REFERENCIA_PECA',
                             'ORDEM_PRINCIPAL', 'QTD',
                             'DT_DIGITACAO', 'DT_CORTE'),

                'o_data': o_data,
            })

            # Grade
            g_header, g_fields, g_data = models.ped_sortimento(cursor, pedido)
            if len(g_data) != 0:
                g_style = {}
                for i in range(1, len(g_fields)):
                    i_column = i + 1
                    g_style[i_column] = \
                        'border-left-style: solid;' \
                        'border-left-width: thin;'

                context.update({
                    'g_headers': g_header,
                    'g_fields': g_fields,
                    'g_data': g_data,
                    'g_style': g_style,
                })

        return context

    def get(self, request, *args, **kwargs):
        if 'pedido' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'pedido' in kwargs:
            form.data['pedido'] = kwargs['pedido']
        if form.is_valid():
            pedido = form.cleaned_data['pedido']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, pedido))
        context['form'] = form
        return render(request, self.template_name, context)


class Expedicao(View):
    Form_class = forms.ExpedicaoForm
    template_name = 'lotes/expedicao.html'
    title_name = 'Expedição'

    def mount_context(
            self, cursor, embarque_de, embarque_ate,
            pedido_tussor, pedido_cliente, cliente,
            deposito, detalhe):
        context = {
            'embarque_de': embarque_de,
            'embarque_ate': embarque_ate,
            'pedido_tussor': pedido_tussor,
            'pedido_cliente': pedido_cliente,
            'cliente': cliente,
            'detalhe': detalhe,
            'deposito': deposito,
        }

        if detalhe == 'g':
            data = models.grade_expedicao(
                cursor,
                embarque_de=embarque_de,
                embarque_ate=embarque_ate,
                pedido_tussor=pedido_tussor,
                pedido_cliente=pedido_cliente,
                cliente=cliente,
                deposito=deposito,
            )
            if len(data) == 0:
                context.update({
                    'msg_erro': 'Nada selecionado',
                })
                return context

            referencia = None
            quant = 0
            data_r = []
            for row in data:
                if referencia is not None and referencia != row['REF']:
                    data_r.append({
                        'ref': referencia,
                        'quant': quant,
                    })
                    quant = 0
                quant += row['QTD']
                referencia = row['REF']
            pprint(data_r)
            context.update({
                'headers': ['ref', 'quant'],
                'fields': ['ref', 'quant'],
                'data': data_r,
            })
            return context

        data = models.ped_expedicao(
            cursor,
            embarque_de=embarque_de,
            embarque_ate=embarque_ate,
            pedido_tussor=pedido_tussor,
            pedido_cliente=pedido_cliente,
            cliente=cliente,
            detalhe=detalhe,
            deposito=deposito,
        )
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nada selecionado',
            })
            return context

        for row in data:
            row['DT_EMISSAO'] = row['DT_EMISSAO'].date()
            row['DT_EMBARQUE'] = row['DT_EMBARQUE'].date()
            row['PEDIDO_VENDA|LINK'] = reverse(
                'producao:pedido__get', args=[row['PEDIDO_VENDA']])
            if detalhe == 'p':
                if row['GTIN_OK'] == 'S':
                    row['GTIN_OK'] = 'Sim'
                else:
                    row['GTIN_OK'] = 'Não'

        if detalhe != 'p':
            group = ['PEDIDO_VENDA', 'PEDIDO_CLIENTE',
                     'DT_EMISSAO', 'DT_EMBARQUE',
                     'CLIENTE']
            totalize_grouped_data(data, {
                'group': group,
                'sum': ['QTD'],
                'count': [],
                'descr': {'REF': 'Total:'},
            })
            group_rowspan(data, group)

        headers = ['Pedido Tussor']
        if detalhe == 'p':
            headers.append('GTIN OK')
        headers.append('Pedido cliente')
        headers.append('Data emissão')
        headers.append('Data embarque')
        headers.append('Cliente')
        if detalhe in ('r', 'c'):
            headers.append('Referência')
        if detalhe == 'c':
            headers.append('Cor')
            headers.append('Tamanho')
        headers.append('Quant.')

        fields = ['PEDIDO_VENDA']
        if detalhe == 'p':
            fields.append('GTIN_OK')
        fields.append('PEDIDO_CLIENTE')
        fields.append('DT_EMISSAO')
        fields.append('DT_EMBARQUE')
        fields.append('CLIENTE')
        if detalhe in ('r', 'c'):
            fields.append('REF')
        if detalhe == 'c':
            fields.append('COR')
            fields.append('TAM')
        fields.append('QTD')

        quant_col = 6
        if detalhe in ('r', 'c'):
            quant_col += 1
        if detalhe == 'c':
            quant_col += 2
        style = {quant_col: 'text-align: right;'}

        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'style': style,
        })
        if detalhe != 'p':
            context.update({
                'group': group,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            embarque_de = form.cleaned_data['embarque_de']
            embarque_ate = form.cleaned_data['embarque_ate']
            pedido_tussor = form.cleaned_data['pedido_tussor']
            pedido_cliente = form.cleaned_data['pedido_cliente']
            cliente = form.cleaned_data['cliente']
            deposito = form.cleaned_data['deposito']
            detalhe = form.cleaned_data['detalhe']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, embarque_de, embarque_ate,
                pedido_tussor, pedido_cliente, cliente,
                deposito, detalhe))
        context['form'] = form
        return render(request, self.template_name, context)
