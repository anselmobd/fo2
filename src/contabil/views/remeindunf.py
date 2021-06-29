from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import group_rowspan

import contabil.forms as forms
import contabil.queries as queries


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
        form.data = form.data.copy()
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

            cursor = db_cursor_so(request)
            data = queries.reme_indu_nf(
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
                    if detalhe in ['I', '1', 'R']:
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

                if detalhe in ['I', '1']:
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
                        15: 'text-align: right;',
                        18: 'text-align: right;',
                    }
                if detalhe == 'R':
                    headers = ('NF. saída', 'Situação', 'Data saída', 'Facção',
                               'OP', 'Pedido', 'Ped. cliente', 'Cliente',
                               'OS', 'Nivel', 'Ref.',
                               'Quant.',
                               'NF retorno', 'Data retorno', 'Quant. retorno',
                               )
                    fields = ('NF', 'ATIVA', 'DT', 'FACCAO',
                              'OP', 'PED', 'PED_CLI', 'CLI',
                              'OS', 'NIVEL', 'REF',
                              'QTD',
                              'NF_RET', 'DT_RET', 'QTD_RET'
                              )
                    style = {
                        12: 'text-align: right;',
                        15: 'text-align: right;',
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

                group = [
                    'NF', 'ATIVA', 'DT', 'FACCAO',
                    'OP', 'PED', 'PED_CLI', 'CLI']
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
