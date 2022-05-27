import operator
import re
from collections import namedtuple
from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import group_rowspan, totalize_grouped_data

import lotes.models

from cd.queries.endereco import query_endereco


class VisaoCd(View):

    def __init__(self):
        self.template_name = 'cd/novo_modulo/visao_cd.html'
        self.title_name = 'Visão do CD'
        self.DataKey = namedtuple('DataKey', 'espaco bloco')

    def mount_context(self):
        context = {}
        cursor = db_cursor_so(self.request)

        enderecos = query_endereco(cursor)

        dados = {}
        for end in enderecos:
            dados_key = self.DataKey(
                espaco=end['espaco'],
                bloco=end['bloco'],
            )
            if dados_key in dados:
                dados[dados_key] += 1
            else:
                dados[dados_key] = 1

        data = [
            {
                'espaco': dados_key.espaco,
                'bloco': dados_key.bloco,
                'qtd_ends': dados[dados_key],
            }
            for dados_key in dados
        ]

        fields = {
            'espaco': 'Espaço',
            'bloco': 'Bloco',
            'qtd_ends': 'Qtd. Endereços',
        }
            # 'andar',
            # 'bloco',
            # 'coluna',
            # 'end',
            # 'order_ap',
            # 'palete',
            # 'prioridade',
            # 'rota',

        context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'data': data,
            # 'group': group,
            # 'style': {3: 'text-align: right;',
            #           4: 'text-align: right;',
            #           5: 'text-align: right;'},
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        data = self.mount_context()
        context.update(data)
        return render(request, self.template_name, context)
