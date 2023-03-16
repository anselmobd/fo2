from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_grouped_data, group_rowspan

import lotes.forms as forms
import lotes.queries.op


class OpPerda(View):

    def __init__(self):
        super().__init__()
        self.Form_class = forms.OpPerdaForm
        self.template_name = 'lotes/perda.html'
        self.title_name = 'Perdas de produção'

    def mount_context(self, cursor, data_de, data_ate, detalhe):
        context = {
            'data_de': data_de,
            'data_ate': data_ate,
            'detalhe': detalhe,
        }
        # Peças em perda
        data = lotes.queries.op.op_perda(cursor, data_de, data_ate, detalhe)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma perda de produção encontrada',
            })
            return context

        for row in data:
            row['OP|LINK'] = reverse('producao:op__get', args=[row['OP']])
            row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])
            row['PERC'] = row['QTD'] / row['QTDOP'] * 100
            row['PERC|DECIMALS'] = 2

        group = ['REF']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['QTD'],
            'count': [],
            'descr': {'OP': 'Total:'},
            'flags': ['NO_TOT_1'],
            'global_sum': ['QTD'],
            'global_descr': {'OP': 'Total geral:'},
        })
        group_rowspan(data, group)

        if detalhe == 'c':
            headers = ('Referência', 'Cor', 'Tamanho', 'OP', 'Quantidade', '%')
            fields = ('REF', 'COR', 'TAM', 'OP', 'QTD', 'PERC')
            style = {
                5: 'text-align: right;',
                6: 'text-align: right;',
            }
        else:
            headers = ('Referência', 'OP', 'Quantidade', '%')
            fields = ('REF', 'OP', 'QTD', 'PERC')
            style = {
                3: 'text-align: right;',
                4: 'text-align: right;',
            }
        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'group': group,
            'style': style,
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
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            detalhe = form.cleaned_data['detalhe']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(
                cursor, data_de, data_ate, detalhe))
        context['form'] = form
        return render(request, self.template_name, context)
