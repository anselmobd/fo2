from pprint import pprint
import datetime

from django.db import connections
from django.shortcuts import render
from django.views import View

import comercial.models


class PainelMetaFaturamento(View):

    def __init__(self):
        self.template_name = 'comercial/painel_meta_faturamento.html'
        self.context = {}

    def mount_context(self):
        cursor = connections['so'].cursor()

        metas = comercial.models.MetaFaturamento.objects.filter(
            data__year=datetime.date.today().year)

        meses = []
        total = {
            'meta': 0,
            'faturado': 0,
            'resultado': 0,
        }
        for meta in metas:
            mes = dict(mes=meta.data, meta=meta.faturamento)
            mes['faturado'] = 0
            mes['resultado'] = 0
            meses.append(mes)
            total['meta'] += meta.faturamento

        self.context.update({
            'meses': meses,
            'total': total,
        })

    def get(self, request, *args, **kwargs):
        self.mount_context()
        return render(request, self.template_name, self.context)
