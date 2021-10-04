from pprint import pprint

from django.shortcuts import render
from django.urls import reverse

from base.views import O2BaseGetPostView

from fo2.connections import db_cursor_so

import comercial.forms as forms
import comercial.queries as queries


class PlanilhaBling(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(PlanilhaBling, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/planilha_bling.html'
        self.title_name = 'Cria planilha Bling'
        self.Form_class = forms.TabelaDePrecoForm
        self.cleaned_data2self = True

    def mount_context(self):
        self.context.update({
            'tabela': self.tabela
        })

        codigo_tabela_chunks = self.tabela.split('.')
        if len(codigo_tabela_chunks) != 3:
            self.context.update({
                'erro': 'Código inválido. '
                        '3 números inteiros separados por ".".'
            })
            return

        for subcodigo_tabela in codigo_tabela_chunks:
            if not subcodigo_tabela.isdigit():
                self.context.update({
                    'erro': 'Cada subcódigo deve ser um número inteiro.'
                })
                return

        codigo_tabela_ints = list(map(int, codigo_tabela_chunks))
        self.tabela = "{:02d}.{:02d}.{:02d}".format(*codigo_tabela_ints)
        self.context.update({
            'tabela': self.tabela
        })

        cursor = db_cursor_so(self.request)

        data = queries.get_tabela_preco(cursor, *codigo_tabela_ints)
        if len(data) == 0:
            self.context.update({
                'erro': 'Tabela não encontrada'
            })
            return

        for row in data:
            row['data_ini_tabela'] = row['data_ini_tabela'].date()
            row['data_fim_tabela'] = row['data_fim_tabela'].date()

        self.context.update({
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
