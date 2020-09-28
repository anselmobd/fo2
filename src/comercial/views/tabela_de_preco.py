from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View

import comercial.forms as forms
import comercial.queries as queries


class TabelaDePreco(View):
    Form_class = forms.TabalaDePrecoForm
    template_name = 'comercial/tabela_de_preco.html'
    title_name = 'Tabela de preços'

    def mount_context(self, cursor, tabela):
        context = {'tabela': tabela}
        codigo_tabela_chunks = tabela.split('.')
        if len(codigo_tabela_chunks) != 3:
            context.update({
                'erro': 'Código inválido. '
                        '3 números inteiros separados por ".".'
            })
            return context

        for subcodigo_tabela in codigo_tabela_chunks:
            if not subcodigo_tabela.isdigit():
                context.update({
                    'erro': 'Cada subcódigo deve ser um número inteiro.'
                })
                return context
        codigo_tabela_ints = list(map(int, codigo_tabela_chunks))
        tabela = "{:02d}.{:02d}.{:02d}".format(*codigo_tabela_ints)
        context = {'tabela': tabela}

        pprint(codigo_tabela_ints)
        data = queries.get_tabela_preco(cursor, *codigo_tabela_ints)
        pprint(data)
        if len(data) == 0:
            context.update({'erro': 'Tabela não encontrada'})
            return context

        for row in data:
            row['data_ini_tabela'] = row['data_ini_tabela'].date()
            row['data_fim_tabela'] = row['data_fim_tabela'].date()

        context.update({
            'headers': [
                'Descrição',
                'Início',
                'Fim',
            ],
            'fields': [
                'descricao',
                'data_ini_tabela',
                'data_fim_tabela',
            ],
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'tabela' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'tabela' in kwargs:
            form.data['tabela'] = kwargs['tabela']
        if form.is_valid():
            tabela = form.cleaned_data['tabela']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, tabela))
        context['form'] = form
        return render(request, self.template_name, context)
