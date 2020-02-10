from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View


class PainelMetaFaturamento(View):

    def __init__(self):
        self.template_name = 'comercial/painel_meta_faturamento.html'
        self.context = {}

    def mount_context(self):
        cursor = connections['so'].cursor()

        meses = [
            {'mes': '01/2020',
             'meta': 12345,
             'faturado': 13455,
             },
            {'mes': '02/2020',
             'meta': 12345,
             'faturado': 13455,
             },
            {'mes': '03/2020',
             'meta': 12345,
             'faturado': 13455,
             },
        ]
        self.context.update({
            'meses': meses,
        })

    def get(self, request, *args, **kwargs):
        self.mount_context()
        return render(request, self.template_name, self.context)
