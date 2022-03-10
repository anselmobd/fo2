from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.forms import FiltroForm

import produto.queries as queries


class RoteirosSemSequ(View):
    Form_class = FiltroForm
    template_name = 'produto/roteiro_sem_sequencia.html'
    title_name = 'Roteiros sem sequência'

    def mount_context(self):
        data = queries.roteiro_sem_sequencia()

        for row in data:
            row['ref|LINK'] = reverse('produto:ref__get', args=[row['ref']])
            row['ref|TARGET'] = '_blank'

        return {
            'headers': ('Referência', 'Tamanho', 'Cor', 
                        'Alternativa', 'Roteiro'),
            'fields': ('ref', 'tam', 'cor',
                        'alt', 'rot'),
            'data': data,
        }

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        context.update(self.mount_context())
        return render(request, self.template_name, context)
