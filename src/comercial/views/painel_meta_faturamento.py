from pprint import pprint
import datetime

from django.db import connections
from django.shortcuts import render
from django.views import View

from utils.functions import dias_mes_data
from utils.models import queryset_to_dict_list_lower
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
        dia_atual = hoje.day
        dias_mes = dias_mes_data(hoje)

        metas = comercial.models.MetaFaturamento.objects.filter(
            data__year=ano_atual)

        faturados = comercial.queries.faturamento_para_meta(
            cursor, ano_atual)
        for faturado in faturados:
            faturado['mes'] = int(faturado['mes'][:2])
        faturados_dict = {
            f['mes']: int(f['valor']/1000) for f in faturados
        }

        devolvidos = comercial.queries.devolucao_para_meta(
            cursor, ano_atual)
        for devolvido in devolvidos:
            devolvido['mes'] = int(devolvido['mes'][:2])
        devolvidos_dict = {
            f['mes']: int(f['valor']/1000) for f in devolvidos
        }

        pedidos = l_q_p.pedido_faturavel_modelo(
            cursor, periodo=f'-{dia_atual}:{dias_mes-dia_atual}')
        total_pedido = 0
        for pedido in pedidos:
            total_pedido += pedido['PRECO']
        total_pedido = int(total_pedido/1000)

        meses = []
        compensar = 0
        planejado_restante = 0
        for meta in metas:
            mes = dict(mes=meta.data, planejado=meta.faturamento)
            mes['imes'] = mes['mes'].month
            mes['faturado'] = (
                faturados_dict.get(mes['imes'], 0) -
                devolvidos_dict.get(mes['imes'], 0)
                )
            if mes['imes'] < mes_atual:
                compensar += mes['planejado'] - mes['faturado']
            else:
                planejado_restante += mes['planejado']
            meses.append(mes)

        for mes in meses:
            if mes['imes'] < mes_atual or compensar < 0:
                mes['meta'] = mes['planejado']
            else:
                mes['meta'] = int(
                    mes['planejado'] + (
                        compensar / planejado_restante * mes['planejado']
                    )
                )
            mes['percentual'] = round(
                mes['faturado'] / mes['meta'] * 100, 1)

        mes = [mes for mes in meses
               if mes['imes'] == mes_atual][0]

        mes['pedidos'] = total_pedido
        mes['perc_pedidos'] = round(
            mes['pedidos'] / mes['meta'] * 100, 1)

        mes['total'] = mes['faturado'] + mes['pedidos']
        mes['perc_total'] = round(
            mes['total'] / mes['meta'] * 100, 1)

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
