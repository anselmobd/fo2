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
        hoje = datetime.date.today()
        ano_atual = hoje.year
        mes_atual = hoje.month

        metas = comercial.models.MetaFaturamento.objects.filter(
            data__year=ano_atual)

        faturados = comercial.queries.faturamento_por_mes_no_ano(
            cursor, ano_atual)
        for faturado in faturados:
            faturado['mes'] = int(faturado['mes'][:2])
        faturados_dict = {
            f['mes']: int(f['valor']/1000) for f in faturados
        }

        meses = []
        total = {
            'meta': 0,
            'faturado': 0,
        }
        for meta in metas:
            mes = dict(mes=meta.data, meta=meta.faturamento)
            mes['imes'] = mes['mes'].month
            mes['faturado'] = faturados_dict.get(mes['imes'], 0)
            mes['percentual'] = int(mes['faturado'] / mes['meta'] * 100)
            meses.append(mes)
            total['meta'] += mes['meta']
            total['faturado'] += mes['faturado']
        total['percentual'] = int(total['faturado'] / total['meta'] * 100)

        self.context.update({
            'meses': meses,
            'total': total,
            'mes_atual': mes_atual,
        })

    def get(self, request, *args, **kwargs):
        self.mount_context()
        return render(request, self.template_name, self.context)
