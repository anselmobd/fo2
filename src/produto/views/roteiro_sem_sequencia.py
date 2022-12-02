from pprint import pprint

from django.urls import reverse

from o2.views.base.get import O2BaseGetView
from utils.forms import FiltroForm

import produto.queries


class RoteirosSemSequ(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(RoteirosSemSequ, self).__init__(*args, **kwargs)
        self.Form_class = FiltroForm
        self.template_name = 'produto/roteiro_sem_sequencia.html'
        self.title_name = 'Roteiros sem sequência'

    def mount_context(self):
        data = produto.queries.roteiro_sem_sequencia()

        for row in data:
            row['ref|LINK'] = reverse('produto:ref__get', args=[row['ref']])
            row['ref|TARGET'] = '_blank'

        self.context.update({
            'headers': ('Referência', 'Tamanho', 'Cor', 
                        'Alternativa', 'Roteiro'),
            'fields': ('ref', 'tam', 'cor',
                        'alt', 'rot'),
            'data': data,
        })
