import datetime

from django.db import connections
from django.shortcuts import render
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
        self.title_name = 'Item no tempo'

    def mount_context(self, cursor, ref, tam, cor, deposito):
        context = {
            'ref': ref,
            'cor': cor,
            'tam': tam,
            'deposito': deposito,
            }

        dados = queries.item_no_tempo(
            cursor, ref, tam, cor, deposito)

        if len(dados) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in dados:
            if (row['doc'] // 1000000) == 702:
                row['data'] = transfo2_num_doc_dt(row['doc'])

        dados = sorted(
            dados, key=lambda i: i['data'], reverse=True)

        estoque_list = queries.get_estoque_dep_ref_cor_tam(
            cursor, deposito, ref, cor, tam)
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
            if (row['doc'] // 1000000) == 702:
                row['tipo'] = 'Ajuste por inventário'
            else:
                if row['proc'] in (
                        'fatu_f146',
                        'fatu_f194',
                        'obrf_f015',
                        'obrf_f025',
                        'obrf_f055',
                        'obrf_f060',
                        ):
                    row['tipo'] = 'Faturamento'
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
                elif row['proc'] in ('pcpc_f230'):
                    row['tipo'] = 'Baixa da OP por estagio'

        context.update({
            'headers': ('Data/hora', 'Usuáro', 'Tipo', 'Documento',
                        'Entrada', 'Saída', 'Estoque'),
            'fields': ('data', 'usuario', 'tipo', 'doc',
                       'qtd_e', 'qtd_s', 'estoque'),
            'style': {
                4: 'text-align: right;',
                5: 'text-align: right;',
                6: 'text-align: right;',
                7: 'text-align: right;',
                },
            'dados': dados,
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
            ref = form.cleaned_data['ref']
            cor = form.cleaned_data['cor']
            tam = form.cleaned_data['tam']
            deposito = form.cleaned_data['deposito']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(cursor, ref, tam, cor, deposito))
        context['form'] = form
        return render(request, self.template_name, context)
