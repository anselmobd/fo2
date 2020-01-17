import datetime
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.views import totalize_data

import lotes.models
import lotes.queries.pedido

from estoque import forms
from estoque import queries
from estoque.functions import (
    transfo2_num_doc,
    transfo2_num_doc_dt,
    )


class ItemNoTempo(View):

    def __init__(self):
        self.Form_class = forms.ItemNoTempoForm
        self.template_name = 'estoque/item_no_tempo.html'
        self.context = {'titulo': 'Item no tempo'}

    def mount_context(self):
        cursor = connections['so'].cursor()

        dados = queries.item_no_tempo(
            cursor, *(self.context[f] for f in [
                'ref', 'tam', 'cor', 'deposito']))
        if len(dados) == 0:
            self.context.update({'erro': 'Nada selecionado'})
            return

        for row in dados:
            if (row['doc'] // 1000000) == 702:
                row['data'] = transfo2_num_doc_dt(row['doc'])

        dados = sorted(
            dados, key=lambda i: i['data'], reverse=True)

        estoque_list = queries.get_estoque_dep_ref_cor_tam(
            cursor, *(self.context[f] for f in [
                'deposito', 'ref', 'cor', 'tam']))
        if len(estoque_list) > 0:
            estoque = estoque_list[0]['estoque']
        else:
            estoque = 0

        estoque_no_tempo = estoque
        for row in dados:
            row['estoque'] = estoque_no_tempo
            estoque_no_tempo -= row['qtd_sinal']

            if row['es'] == 'E':
                row['qtd_e'] = row['qtd']
                row['qtd_s'] = '.'
            else:
                row['qtd_e'] = '.'
                row['qtd_s'] = f"({row['qtd']})"

            row['tipo'] = row['proc']
            tipo_doc = ''
            if (row['doc'] // 1000000) == 702:
                row['tipo'] = 'Ajuste por inventário'
            else:
                if row['proc'] in (
                        'fatu_f146',
                        'fatu_f194',
                        'obrf_f025',
                        'obrf_f055',
                        'obrf_f060',
                        ):
                    row['tipo'] = 'Nota fiscal de saída'
                    tipo_doc = 'nfs'
                elif row['proc'] in ('obrf_f015'):
                    row['tipo'] = 'Nota fiscal de entrada'
                    tipo_doc = 'nfe'
                elif row['proc'] in ('estq_f015'):
                    row['tipo'] = 'Movimentação de estoques'
                elif row['proc'] in ('estq_f950'):
                    row['tipo'] = 'Acerto de estoques'
                elif row['proc'] in (
                        'obrf_f484',
                        'pcpc_f046',
                        'pcpc_f072',
                        ):
                    row['tipo'] = 'Baixa da OC por pacote'
                    tipo_doc = 'op'
                elif row['proc'] in ('pcpc_f230'):
                    row['tipo'] = 'Baixa da OP por estagio'
                    tipo_doc = 'op'

            if tipo_doc == '':
                row['ped'] = '.'
                row['cliente'] = '.'
            else:
                row['doc|TARGET'] = '_blank'

            if tipo_doc == 'nfs':
                row['doc|LINK'] = reverse(
                    'contabil:nota_fiscal__get', args=[row['doc']])
            elif tipo_doc == 'op':
                row['doc|LINK'] = reverse(
                    'producao:op__get', args=[row['doc']])

            if row['ped'] is None:
                row['ped'] = '.'
            if row['ped'] != '.':
                row['ped|TARGET'] = '_blank'
                row['ped|LINK'] = reverse(
                    'producao:pedido__get', args=[row['ped']])

            if row['cnpj_9'] == 0:
                row['cliente'] = '.'

            if row['cliente'] != '.':
                if row['fantasia'] is not None and row['fantasia'] != '':
                    row['cliente'] = row['fantasia']

        self.context.update({
            'headers': ('Data/hora', 'Usuáro', 'Tipo de movimentação',
                        'Cliente', 'Documento', 'Pedido',
                        'Entrada', 'Saída', 'Estoque'),
            'fields': ('data', 'usuario', 'tipo',
                       'cliente', 'doc', 'ped',
                       'qtd_e', 'qtd_s', 'estoque'),
            'style': {
                5: 'text-align: right;',
                6: 'text-align: right;',
                7: 'text-align: right;',
                8: 'text-align: right;',
                9: 'text-align: right;',
                },
            'dados': dados,
            })

        p_dados = lotes.queries.pedido.pedido_faturavel_modelo(
            cursor, cached=False,
            **{f: self.context[f] for f in ['ref', 'cor', 'tam']}
            )

        if len(p_dados) > 0:
            p_dados.insert(0, p_dados[0].copy())
            for i, row in enumerate(p_dados):
                if i == 0:
                    row['PEDIDO'] = ''
                    row['DATA'] = ''
                    row['CLIENTE'] = ''
                    row['FAT'] = ''
                    row['QTD_AFAT'] = ''
                    estoque_no_tempo = estoque
                else:
                    row['PEDIDO|TARGET'] = '_blank'
                    row['PEDIDO|LINK'] = reverse(
                        'producao:pedido__get', args=[row['PEDIDO']])
                    row['DATA'] = row['DATA'].date()
                    row['QTD_AFAT'] = row['QTD'] - row['QTD_FAT']
                    estoque_no_tempo -= row['QTD_AFAT']

                row['ESTOQUE'] = estoque_no_tempo

            self.context.update({
                'p_headers': [
                    'Nº do pedido', 'Data de embarque', 'Cliente',
                    'Faturamento', 'Quant. pedida', 'Estoque'],
                'p_fields': [
                    'PEDIDO', 'DATA', 'CLIENTE',
                    'FAT', 'QTD_AFAT', 'ESTOQUE'],
                'p_style': {
                    5: 'text-align: right;',
                    6: 'text-align: right;',
                    },
                'p_dados': p_dados,
                })

        oc_dados = lotes.models.quant_estagio(
            cursor, only=[57, 63], group='o',
            **{f: self.context[f] for f in ['ref', 'cor', 'tam']})

        if len(oc_dados) > 0:

            for row in oc_dados:
                row['ORDEM_PRODUCAO|TARGET'] = '_blank'
                row['ORDEM_PRODUCAO|LINK'] = reverse(
                    'producao:op__get', args=[row['ORDEM_PRODUCAO']])

            self.context.update({
                'oc_headers': [
                    'OP', 'Quantidade'],
                'oc_fields': [
                    'ORDEM_PRODUCAO', 'QUANT'],
                'oc_style': {
                    2: 'text-align: right;',
                    },
                'oc_dados': oc_dados,
                })

        op_dados = lotes.models.quant_estagio(
            cursor, less=[57, 63], group='o',
            **{f: self.context[f] for f in ['ref', 'cor', 'tam']})

        if len(op_dados) > 0:

            for row in op_dados:
                row['ORDEM_PRODUCAO|TARGET'] = '_blank'
                row['ORDEM_PRODUCAO|LINK'] = reverse(
                    'producao:op__get', args=[row['ORDEM_PRODUCAO']])

            self.context.update({
                'op_headers': [
                    'OP', 'Quantidade'],
                'op_fields': [
                    'ORDEM_PRODUCAO', 'QUANT'],
                'op_style': {
                    2: 'text-align: right;',
                    },
                'op_dados': op_dados,
                })

    def cleanned_fields_to_context(self):
        for field in self.context['form'].fields:
            self.context[field] = self.context['form'].cleaned_data[field]

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            self.context['form'] = self.Form_class(self.context)
            self.mount_context()
        return render(request, self.template_name, self.context)
