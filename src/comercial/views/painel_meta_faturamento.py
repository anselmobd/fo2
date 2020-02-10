from pprint import pprint
import datetime

from django.db import connections
from django.shortcuts import render
from django.views import View

import comercial.models
import comercial.queries


class PainelMetaFaturamento(View):

    def __init__(self):
        self.template_name = 'comercial/painel_meta_faturamento.html'
        self.context = {}

    def mount_context(self):
        cursor = connections['so'].cursor()
        ano_atual = datetime.date.today().year

        metas = comercial.models.MetaFaturamento.objects.filter(
            data__year=ano_atual)

        faturados = comercial.queries.faturamento_por_mes_no_ano(
            cursor, ano_atual)
        for faturado in faturados:
            faturado['mes'] = datetime.date(
                ano_atual,
                int(faturado['mes'][:2]),
                1)
        faturados_dict = {
            f['mes']: int(f['valor']/1000) for f in faturados
        }

        meses = []
        total = {
            'meta': 0,
            'faturado': 0,
            'resultado': 0,
        }
        for meta in metas:
            mes = dict(mes=meta.data, meta=int(meta.faturamento))
            mes['faturado'] = faturados_dict.get(mes['mes'], 0)
            mes['resultado'] = mes['faturado'] - mes['meta']
            meses.append(mes)
            total['meta'] += mes['meta']
            total['faturado'] += mes['faturado']
            total['resultado'] += mes['resultado']

        self.context.update({
            'meses': meses,
            'total': total,
        })

    def get(self, request, *args, **kwargs):
        self.mount_context()
        return render(request, self.template_name, self.context)
