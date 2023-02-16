from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.forms import FiltroForm
from utils.views import group_rowspan

import produto.queries as queries


class MultiplasColecoes(View):

    def __init__(self):
        super().__init__()
        self.Form_class = FiltroForm
        self.template_name = 'produto/multiplas_colecoes.html'
        self.title_name = 'Múltiplas coleções em modelo'

    def mount_context(self, cursor):
        context = {}

        # Informações básicas
        data = queries.multiplas_colecoes(cursor)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum erro de múltiplas coleções em modelos.',
            })
        else:
            link = ('REF')
            for row in data:
                row['LINK'] = reverse('produto:ref__get', args=[row['REF']])

            group = ['MODELO', 'COLECOES']
            group_rowspan(data, group)

            context.update({
                'headers': ('Modelo', 'Nº coleções', 'Coleção', 'Descrição',
                            'Referência', 'Descrição'),
                'fields': ('MODELO', 'COLECOES', 'COLECAO', 'DESCR_COLECAO',
                           'REF', 'DESCR'),
                'data': data,
                'link': link,
                'group': group,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = db_cursor_so(request)
        context.update(self.mount_context(cursor))
        return render(request, self.template_name, context)
