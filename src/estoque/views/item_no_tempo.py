import datetime
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.views import totalize_data

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

        for row in dados:
            row['estoque'] = estoque
            estoque -= row['qtd_sinal']

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
                    tipo_doc = 'nf'
                elif row['proc'] in ('obrf_f015'):
                    row['tipo'] = 'Nota fiscal de entrada'
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

            if tipo_doc == 'nf':
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
                },
            'dados': dados,
            })

        return

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
