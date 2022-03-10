from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.forms import FiltroForm

import produto.queries as queries


class RoteirosSemSequ(View):
    Form_class = FiltroForm
    template_name = 'produto/roteiro_sem_sequencia.html'
    title_name = 'Roteiros sem sequência'

    def mount_context(self, cursor):
        context = {}
        data = queries.roteiro_sem_sequencia(cursor)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum roteiro sem sequência.',
            })
        else:
            for row in data:
                row['ref|LINK'] = reverse('produto:ref__get', args=[row['ref']])

            context.update({
                'headers': ('Referência', 'Tamanho', 'Cor', 
                            'Alternativa', 'Roteiro'),
                'fields': ('ref', 'tam', 'cor',
                           'alt', 'rot'),
                'data': data,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = db_cursor_so(request)
        context.update(self.mount_context(cursor))
        return render(request, self.template_name, context)
