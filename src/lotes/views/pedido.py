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
                            'Cliente', 'Código do pedido no cliente',
                            'Status do pedido', 'Situação da venda',
                            'Observação'),
                'fields': ('DT_EMISSAO', 'DT_EMBARQUE',
                           'CLIENTE', 'PEDIDO_CLIENTE',
                           'STATUS_PEDIDO', 'SITUACAO_VENDA',
                           'OBSERVACAO'),
                'data': data,
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
                context.update({
                    'g_headers': g_header,
                    'g_fields': g_fields,
                    'g_data': g_data,
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
            pedido_tussor, pedido_cliente, cliente):
        context = {
            'embarque_de': embarque_de,
            'embarque_ate': embarque_ate,
            'pedido_tussor': pedido_tussor,
            'pedido_cliente': pedido_cliente,
            'cliente': cliente,
        }

        data = models.ped_expedicao(
            cursor,
            embarque_de=embarque_de,
            embarque_ate=embarque_ate,
            pedido_tussor=pedido_tussor,
            pedido_cliente=pedido_cliente,
            cliente=cliente
        )
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nada selecionado',
            })
            return context

        for row in data:
            row['DT_EMISSAO'] = row['DT_EMISSAO'].date()
            row['DT_EMBARQUE'] = row['DT_EMBARQUE'].date()

        group = ['PEDIDO_VENDA', 'PEDIDO_CLIENTE',
                 'DT_EMISSAO', 'DT_EMBARQUE',
                 'CLIENTE']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['QTD'],
            'count': [],
            'descr': {'TAM': 'Total:'},
        })
        group_rowspan(data, group)

        context.update({
            'headers': ('Pedido Tussor', 'Pedido cliente',
                        'Data emissão', 'Data embarque',
                        'Cliente', 'Referência', 'Cor', 'Tamanho', 'Quant.'),
            'fields': ('PEDIDO_VENDA', 'PEDIDO_CLIENTE',
                       'DT_EMISSAO', 'DT_EMBARQUE',
                       'CLIENTE', 'REF', 'COR', 'TAM', 'QTD'),
            'data': data,
            'group': group,
            'style': {9: 'text-align: right;'},
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
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, embarque_de, embarque_ate,
                pedido_tussor, pedido_cliente, cliente))
        context['form'] = form
        return render(request, self.template_name, context)
