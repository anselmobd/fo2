from pprint import pprint
import urllib

from django.shortcuts import render
from django.urls import reverse
from django.db import connections
from django.views import View

from fo2.template import group_rowspan
from utils.views import totalize_grouped_data

import contabil.forms as forms
import contabil.models as models


def index(request):
    context = {}
    return render(request, 'contabil/index.html', context)


class InfAdProd(View):
    Form_class = forms.InfAdProdForm
    template_name = 'contabil/infadprod.html'
    title_name = 'Itens de pedido'

    def mount_context(self, pedido):
        context = {
            'pedido': pedido,
        }
        cursor = connections['so'].cursor()
        data = models.infadprod_por_pedido(cursor, pedido)
        if len(data) == 0:
            context['erro'] = 'Pedido não encontrado'
        else:
            for row in data:
                row['VALOR_TOTAL'] = row['VALOR'] * row['QTD']
                if row['COUNT_GTIN'] == 0:
                    row['COUNT_GTIN'] = '-'
                elif row['COUNT_GTIN'] == 1:
                    row['COUNT_GTIN'] = 'Único'
                else:
                    row['COUNT_GTIN|LINK'] = '{}?{}'.format(
                        reverse('produto:gtin'),
                        urllib.parse.urlencode({
                            'gtin': row['GTIN'],
                        }))
                    row['COUNT_GTIN|TARGET'] = '_BLANK'

            totalize_grouped_data(data, {
                'group': [],
                'sum': ['QTD', 'VALOR_TOTAL'],
                'global_sum': ['QTD', 'VALOR_TOTAL'],
                'global_descr': {'REF': 'Totais:'},
                'row_style': 'font-weight: bold;',
            })

            for row in data:
                row['VALOR|DECIMALS'] = 2
                row['VALOR_TOTAL|DECIMALS'] = 2
            row = data[0]
            context.update({
                'cliente': row['CLIENTE'],
                'headers': ('Nível', 'Ref.', 'Cor', 'Tam.', 'Quantidade',
                            'Valor unitário', 'Valor total',
                            'Ref.Clie.(infAdProd)',
                            'Descr.Clie.(infAdProd)',
                            'GTIN', '#', 'Narrativa'),
                'fields': ('NIVEL', 'REF', 'COR', 'TAM', 'QTD',
                           'VALOR', 'VALOR_TOTAL',
                           'INFADPROD', 'DESCRCLI',
                           'GTIN', 'COUNT_GTIN', 'NARRATIVA'),
                'style': {
                    5: 'text-align: right;',
                    6: 'text-align: right;',
                    7: 'text-align: right;',
                },
                'data': data,
            })
        return context

    def get(self, request, *args, **kwargs):
        if 'pedido' in kwargs and kwargs['pedido'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'pedido' in kwargs and kwargs['pedido'] is not None:
            form.data['pedido'] = kwargs['pedido']
        if form.is_valid():
            pedido = form.cleaned_data['pedido']
            context.update(self.mount_context(pedido))
        context['form'] = form
        return render(request, self.template_name, context)


class RemessaIndustr(View):
    Form_class = forms.RemessaIndustrForm
    template_name = 'contabil/remeindu.html'
    title_name = 'Industrialização por OP'

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.Form_class(request.POST)
        context = {'titulo': self.title_name}
        if form.is_valid():
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            faccao = form.cleaned_data['faccao']
            cliente = form.cleaned_data['cliente']
            pedido = form.cleaned_data['pedido']
            pedido_cliente = form.cleaned_data['pedido_cliente']
            op = form.cleaned_data['op']
            retorno = form.cleaned_data['retorno']
            detalhe = form.cleaned_data['detalhe']

            cursor = connections['so'].cursor()
            data = models.reme_indu(
                cursor, dt_saida_de=data_de, dt_saida_ate=data_ate,
                faccao=faccao, cliente=cliente,
                pedido=pedido, pedido_cliente=pedido_cliente, op=op,
                retorno=retorno, detalhe=detalhe)
            if len(data) == 0:
                context['erro'] = 'Remessa não encontrada'
            else:
                total_pecas = 0
                for row in data:
                    total_pecas += row['QTD']
                    row['DT'] = row['DT'].date()
                    if row['DT_RET'] is None:
                        row['DT_RET'] = '-'
                        row['NF_RET'] = '-'
                        row['QTD_RET'] = '-'
                    else:
                        row['DT_RET'] = row['DT_RET'].date()
                    if row['PED'] == 0:
                        row['PED'] = '-'
                        row['CLI'] = '-'
                    if row['PED_CLI'] is None:
                        row['PED_CLI'] = '-'
                    if row['TAM'] is None:
                        row['TAM'] = '-'
                    row['OP|LINK'] = reverse(
                        'producao:op__get', args=[row['OP']])
                    row['OS|LINK'] = reverse(
                        'producao:os__get', args=[row['OS']])
                    if row['PED'] != '-':
                        row['PED|LINK'] = reverse(
                            'producao:pedido__get', args=[row['PED']])
                context.update({
                    'data_de': data_de,
                    'data_ate': data_ate,
                    'faccao': faccao,
                    'cliente': cliente,
                    'pedido': pedido,
                    'pedido_cliente': pedido_cliente,
                    'retorno': retorno,
                    'detalhe': detalhe,
                    'total_pecas': total_pecas,
                    'headers': ('OP', 'Ref.', 'Cor', 'Tam.', 'OS', 'Quant.',
                                'Data saída', 'NF. saída', 'Facção',
                                'Data retorno', 'NF retorno', 'Quant. retorno',
                                'Pedido', 'Ped. cliente', 'Cliente'),
                    'fields': ('OP', 'REF', 'COR', 'TAM', 'OS', 'QTD',
                               'DT', 'NF', 'FACCAO',
                               'DT_RET', 'NF_RET', 'QTD_RET',
                               'PED', 'PED_CLI', 'CLI'),
                    'data': data,
                })

        context['form'] = form
        return render(request, self.template_name, context)


class RemessaIndustrNF(View):
    Form_class = forms.RemessaIndustrNFForm
    template_name = 'contabil/remeindunf.html'
    title_name = 'Industrialização por NF de remessa'

    def get(self, request, *args, **kwargs):
        if 'nf' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.Form_class(request.POST)
        context = {'titulo': self.title_name}
        if 'nf' in kwargs:
            if kwargs['nf'] is not None:
                form.data['nf'] = kwargs['nf']
                form.data['retorno'] = 'T'
            if kwargs['detalhe'] is not None:
                form.data['detalhe'] = kwargs['detalhe']
        if form.is_valid():
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            faccao = form.cleaned_data['faccao']
            cliente = form.cleaned_data['cliente']
            pedido = form.cleaned_data['pedido']
            pedido_cliente = form.cleaned_data['pedido_cliente']
            op = form.cleaned_data['op']
            retorno = form.cleaned_data['retorno']
            situacao = form.cleaned_data['situacao']
            data_ret_de = form.cleaned_data['data_ret_de']
            data_ret_ate = form.cleaned_data['data_ret_ate']
            nf_ret = form.cleaned_data['nf_ret']
            nf = form.cleaned_data['nf']
            detalhe = form.cleaned_data['detalhe']

            cursor = connections['so'].cursor()
            data = models.reme_indu_nf(
                cursor, dt_saida_de=data_de, dt_saida_ate=data_ate,
                faccao=faccao, cliente=cliente,
                pedido=pedido, pedido_cliente=pedido_cliente, op=op,
                retorno=retorno, situacao=situacao,
                dt_entrada_de=data_ret_de, dt_entrada_ate=data_ret_ate,
                nf_entrada=nf_ret, nf_saida=nf, detalhe=detalhe)
            if len(data) == 0:
                context['erro'] = 'Remessa não encontrada'
            else:
                total_pecas = 0
                for row in data:
                    if detalhe == 'I':
                        total_pecas += row['QTD']
                    row['DT'] = row['DT'].date()
                    if row['DT_RET'] is None:
                        row['DT_RET'] = '-'
                        row['NF_RET'] = '-'
                        row['QTD_RET'] = '-'
                    else:
                        row['DT_RET'] = row['DT_RET'].date()
                    if row['PED_CLI'] is None:
                        row['PED_CLI'] = '-'
                    if row['OP'] is None:
                        row['OP'] = '-'
                    else:
                        row['OP|LINK'] = reverse(
                            'producao:op__get', args=[row['OP']])
                    if row['OS'] is None:
                        row['OS'] = '-'
                    else:
                        row['OS|LINK'] = reverse(
                            'producao:os__get', args=[row['OS']])
                    if row['PED'] is None:
                        row['PED'] = '-'
                        row['CLI'] = '-'
                    else:
                        row['PED|LINK'] = reverse(
                            'producao:pedido__get', args=[row['PED']])
                    row['NF|LINK'] = reverse(
                        'contabil:remeindunf__get', args=[row['NF'], 'I'])
                    row['NF|TARGET'] = '_BLANK'
                    if row['SITUACAO'] == 1:
                        if row['NF_DEVOLUCAO'] is None:
                            row['ATIVA'] = 'Ativa'
                        else:
                            row['ATIVA'] = row['NF_DEVOLUCAO']
                    else:
                        row['ATIVA'] = 'Cancelada'

                if detalhe == 'I':
                    headers = ('NF. saída', 'Situação', 'Data saída', 'Facção',
                               'OP', 'Pedido', 'Ped. cliente', 'Cliente',
                               'OS', 'Seq.', 'Nivel', 'Ref.', 'Cor', 'Tam.',
                               'Quant.',
                               'NF retorno', 'Data retorno', 'Quant. retorno',
                               )
                    fields = ('NF', 'ATIVA', 'DT', 'FACCAO',
                              'OP', 'PED', 'PED_CLI', 'CLI',
                              'OS', 'SEQ', 'NIVEL', 'REF', 'COR', 'TAM',
                              'QTD',
                              'NF_RET', 'DT_RET', 'QTD_RET'
                              )
                    style = {
                        14: 'text-align: right;',
                        17: 'text-align: right;',
                    }
                else:
                    headers = ('NF. saída', 'Situação', 'Data saída', 'Facção',
                               'OP', 'Pedido', 'Ped. cliente', 'Cliente',
                               'OS', 'NF retorno', 'Data retorno',
                               )
                    fields = ('NF', 'ATIVA', 'DT', 'FACCAO',
                              'OP', 'PED', 'PED_CLI', 'CLI',
                              'OS', 'NF_RET', 'DT_RET'
                              )
                    style = {}

                group = ['NF', 'DT', 'FACCAO', 'OP', 'PED', 'PED_CLI', 'CLI']
                group_rowspan(data, group)

                context.update({
                    'data_de': data_de,
                    'data_ate': data_ate,
                    'faccao': faccao,
                    'cliente': cliente,
                    'pedido': pedido,
                    'pedido_cliente': pedido_cliente,
                    'retorno': retorno,
                    'data_ret_de': data_ret_de,
                    'data_ret_ate': data_ret_ate,
                    'nf_ret': nf_ret,
                    'nf': nf,
                    'detalhe': detalhe,
                    'total_pecas': total_pecas,
                    'headers': headers,
                    'fields': fields,
                    'data': data,
                    'group': group,
                    'style': style,
                })

        context['form'] = form
        return render(request, self.template_name, context)
