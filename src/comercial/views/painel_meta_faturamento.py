from pprint import pprint
import datetime

from django.db import connections
from django.shortcuts import render
from django.views import View

from utils.functions import dias_mes_data
from utils.functions.models import queryset_to_dict_list_lower
from utils.views import totalize_data

import lotes.queries.pedido as l_q_p

import comercial.models
import comercial.queries


class PainelMetaFaturamento(View):

    def __init__(self):
        self.template_name = 'comercial/painel_meta_faturamento.html'
        self.context = {}

    def mount_context(self):
        cursor = connections['so'].cursor()
        hoje = datetime.datetime.now()
        ano_atual = hoje.year
        mes_atual = hoje.month

        meses, _ = comercial.queries.dados_meta_no_ano(cursor, hoje)

        mes = [mes for mes in meses
               if mes['imes'] == mes_atual][0]
        mes['perc_faturado'] = round(
            mes['faturado'] / mes['meta'] * 100, 1)
        mes['perc_pedido'] = round(
            mes['pedido'] / mes['meta'] * 100, 1)
        mes['total'] = mes['faturado'] + mes['pedido']

        pendencias = comercial.models.PendenciaFaturamento.objects.filter(
            mes__year=ano_atual, mes__month=mes_atual, ).order_by('ordem')
        pends = queryset_to_dict_list_lower(pendencias)
        if len(pends) != 0:
            for pend in pends:
                pend['total'] = False
                if pend['obs'] is None:
                    pend['obs'] = ''

            totalize_data(pends, {
                'sum': ['valor'],
                'count': [],
                'descr': {'pendencia': 'Total:'},
            })
            pends[-1]['total'] = True

        self.context.update({
            'mes': mes,
            'hoje': hoje,
            'pends': pends,
        })

    def get(self, request, *args, **kwargs):
        self.mount_context()
        return render(request, self.template_name, self.context)
