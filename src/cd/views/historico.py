from pprint import pprint

from django.db import connection
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.views import totalize_data

import cd.queries as queries
import cd.forms


class Historico(View):

    def __init__(self):
        self.Form_class = cd.forms.HistoricoForm
        self.template_name = 'cd/historico.html'
        self.title_name = 'Histórico de OP'

    def mount_context(self, cursor, op):
        context = {
            'op': op,
            }

        data = queries.historico(cursor, op)
        if len(data) == 0:
            context.update({'erro': 'Sem lotes ativos'})
            return context
        for row in data:
            if row['dt'] is None:
                row['dt'] = 'Nunca inventariado'
            if row['endereco'] is None:
                if row['usuario'] is None:
                    row['endereco'] = '-'
                else:
                    row['endereco'] = 'SAIU!'
            if row['usuario'] is None:
                row['usuario'] = '-'
        context.update({
            'headers': ('Data', 'Qtd. de lotes', 'Endereço', 'Usuário'),
            'fields': ('dt', 'qtd', 'endereco', 'usuario'),
            'data': data,
        })

        data = queries.historico_detalhe(cursor, op)
        for row in data:
            if row['dt'] is None:
                row['dt'] = 'Nunca inventariado'
            if row['endereco'] is None:
                if row['usuario'] is None:
                    row['endereco'] = '-'
                else:
                    row['endereco'] = 'SAIU!'
                row['qtd_end'] = 0
            else:
                row['qtd_end'] = row['qtd']
            if row['usuario'] is None:
                row['usuario'] = '-'
            row['lote|LINK'] = reverse(
                'cd:historico_lote', args=[row['lote']])
            if row['estagio'] == 999:
                row['estagio'] = '-'
                row['qtd'] = 0

        totalize_data(data, {
            'sum': ['qtd_end', 'qtd'],
            'count': [],
            'descr': {'endereco': 'Totais:'}})

        for row in data:
            if row['qtd_end'] == 0:
                row['qtd_end'] = '-'
            if row['qtd'] == 0:
                row['qtd'] = '-'

        context.update({
            'd_headers': ('Lote', 'Última data', 'Endereço', 'Quant.', 'Estágio', 'Quant.', 'Usuário'),
            'd_fields': ('lote', 'dt', 'endereco', 'qtd_end', 'estagio', 'qtd', 'usuario'),
            'd_data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'op' in kwargs and kwargs['op'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'op' in kwargs and kwargs['op'] is not None:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = connection.cursor()
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)
