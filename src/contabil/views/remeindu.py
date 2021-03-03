from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

import contabil.forms as forms
import contabil.queries as queries


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
            data_ret_de = form.cleaned_data['data_ret_de']
            data_ret_ate = form.cleaned_data['data_ret_ate']
            nf_ret = form.cleaned_data['nf_ret']
            nf = form.cleaned_data['nf']
            detalhe = form.cleaned_data['detalhe']

            cursor = db_cursor_so(self.request)
            data = queries.reme_indu(
                cursor, dt_saida_de=data_de, dt_saida_ate=data_ate,
                faccao=faccao, cliente=cliente,
                pedido=pedido, pedido_cliente=pedido_cliente, op=op,
                retorno=retorno,
                dt_entrada_de=data_ret_de, dt_entrada_ate=data_ret_ate,
                nf_entrada=nf_ret, nf_saida=nf, detalhe=detalhe)
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
