import datetime
from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.decorators import CacheGet
from utils.functions.models.dictlist import queryset_to_dictlist_lower
from utils.views import totalize_data

import lotes.queries.pedido as l_q_p

import comercial.models
import comercial.queries


class PainelMetaFaturamento(View):

    def __init__(self):
        self.template_name = 'comercial/painel_meta_faturamento.html'
        self.context = {}

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        hoje = datetime.datetime.now()  # + datetime.timedelta(days=1)
        ano_atual = hoje.year
        mes_atual = hoje.month

        # se:
        # - a função foi decorada com caching_function; E
        # - foi indicado o uso de caching_params
        # cg = CacheGet()
        # msg_erro, meses, _ = cg.get_result(
        #     comercial.queries.dados_meta_no_ano(cursor, hoje.date())
        # )

        # se:
        # - a função NÃO foi decorada com caching_function; OU
        # - NÃO foi indicado o uso de caching_params
        # msg_erro, meses, _ = comercial.queries.dados_meta_no_ano(cursor, hoje.date())

        msg_erro, meses, _ = comercial.queries.dados_meta_no_ano_control(
            cursor, hoje.date())

        if msg_erro:
            self.context.update({
                'msg_erro': msg_erro,
            })
            return

        mes = [mes for mes in meses
               if mes['imes'] == mes_atual][0]
        mes['perc_faturado'] = round(
            mes['faturado'] / mes['meta'] * 100, 1)
        mes['perc_pedido'] = round(
            mes['pedido'] / mes['meta'] * 100, 1)
        mes['total'] = mes['faturado'] + mes['pedido']

        pendencias = comercial.models.PendenciaFaturamento.objects.filter(
            mes__year=ano_atual, mes__month=mes_atual, ).order_by('ordem')
        pends = queryset_to_dictlist_lower(pendencias)
        if len(pends) != 0:
            for pend in pends:
                pend['total'] = False
                if pend['obs'] is None:
                    pend['obs'] = ''

            totalize_data(pends, {
                'sum': ['valor'],
                'descr': {'pendencia': 'Total:'},
            })
            pends[-1]['total'] = True

        self.context.update({
            'mes': mes,
            'hoje': hoje,
            'pends': pends,
        })

    def get(self, request, *args, **kwargs):
        self.request = request
        self.mount_context()
        return render(request, self.template_name, self.context)
