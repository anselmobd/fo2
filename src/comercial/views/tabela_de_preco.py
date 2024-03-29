from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

import comercial.forms as forms
import comercial.queries as queries


class TabelaDePreco(View):

    def __init__(self):
        super().__init__()
        self.Form_class = forms.TabelaDePrecoForm
        self.template_name = 'comercial/tabela_de_preco.html'
        self.title_name = 'Tabela de preços'

    def mount_context(self, cursor, tabela):
        context = {'tabela': tabela}
        codigo_tabela_chunks = tabela.split('.')
        if len(codigo_tabela_chunks) != 3:
            context.update({
                'erro': 'Código inválido. '
                        '3 números inteiros separados por ".".'
            })

            data = queries.get_tabela_preco(cursor, order='a')
            if len(data) == 0:
                context.update({'erro': 'Sem tabelas de preço'})
                return context

            for row in data:
                row['tabela'] = "{:02d}.{:02d}.{:02d}".format(
                    row['col_tabela_preco'],
                    row['mes_tabela_preco'],
                    row['seq_tabela_preco'],
                )
                row['tabela|LINK'] = reverse(
                    'comercial:tabela_de_preco__get',
                    args=[row['tabela']]
                )
                row['data_ini_tabela'] = row['data_ini_tabela'].date()
                row['data_fim_tabela'] = row['data_fim_tabela'].date()

            context.update({
                'headers': [
                    'Tabela',
                    'Descrição',
                    'Início',
                    'Fim',
                ],
                'fields': [
                    'tabela',
                    'descricao',
                    'data_ini_tabela',
                    'data_fim_tabela',
                ],
                'data': data,
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

        data = queries.get_tabela_preco(cursor, *codigo_tabela_ints)
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

        i_data = queries.itens_tabela_preco(cursor, *codigo_tabela_ints)
        if len(i_data) == 0:
            context.update({'erro': 'Tabela vazia'})
            return context

        context.update({
            'i_headers': [
                'Referência',
                'Descrição',
                'Valor',
            ],
            'i_fields': [
                'grupo_estrutura',
                'descr_referencia',
                'val_tabela_preco'
            ],
            'i_data': i_data,
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
        form.data = form.data.copy()
        if 'tabela' in kwargs:
            form.data['tabela'] = kwargs['tabela']
        if form.is_valid():
            tabela = form.cleaned_data['tabela']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, tabela))
        context['form'] = form
        return render(request, self.template_name, context)
