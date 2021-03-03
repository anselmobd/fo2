import datetime

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_data

from estoque import forms, queries
from estoque.functions import transfo2_num_doc


class EstoqueNaData(View):

    def __init__(self):
        self.Form_class = forms.EstoqueNaDataForm
        self.template_name = 'estoque/estoque_na_data.html'
        self.title_name = 'Estoque na data'

    def mount_context(self, cursor, ref, tam, cor, data, hora, deposito):
        context = {
            'cor': cor,
            'tam': tam,
            'data': data,
            'hora': hora,
            'deposito': deposito,
            }

        modelo = None
        if len(ref) % 5 == 0:
            context.update({
                'ref': ref,
            })
        else:
            modelo = ref.lstrip("0")
            ref = ''
            context.update({
                'modelo': modelo,
            })

        if data < datetime.date(2018, 11, 1):
            context.update({'erro': 'Erro: Dara mínima = 01/11/2018'})
            return context

        num_doc = transfo2_num_doc(data, hora)

        dados = queries.estoque_na_data(
            cursor, ref, modelo, tam, cor, data, hora, num_doc, deposito)

        if len(dados) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in dados:
            row['stq_data'] = row['stq'] - row['trans'] - row['ajuste']

        totalize_data(dados, {
            'sum': ['stq_data', 'trans', 'ajuste', 'stq'],
            'count': [],
            'descr': {'tam': 'Totais:'},
            'row_style': 'font-weight: bold;',
            })

        context.update({
            'headers': ('Depósito', 'Referência', 'Cor', 'Tamanho',
                        'Estoque na data', 'Transações', 'Ajustes', 'Estoque'),
            'fields': ('dep', 'ref', 'cor', 'tam',
                       'stq_data', 'trans', 'ajuste', 'stq'),
            'style': {
                5: 'text-align: right;',
                6: 'text-align: right;',
                7: 'text-align: right;',
                8: 'text-align: right;',
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
            data = form.cleaned_data['data']
            hora = form.cleaned_data['hora']
            deposito = form.cleaned_data['deposito']
            cursor = db_cursor_so(request)
            context.update(
                self.mount_context(
                    cursor, ref, tam, cor, data, hora, deposito))
        context['form'] = form
        return render(request, self.template_name, context)
