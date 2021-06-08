import datetime
from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions import dias_mes_data
from utils.functions.models import queryset_to_dict_list_lower
from utils.views import totalize_data

import lotes.queries.pedido as l_q_p

import comercial.forms
import comercial.models
import comercial.queries


class PedidosParaMeta(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(PedidosParaMeta, self).__init__(*args, **kwargs)
        self.Form_class = comercial.forms.PedidosParaMetaForm
        self.template_name = 'comercial/pedidos_para_meta.html'
        self.title_name = 'Pedidos no mês'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        ano = self.form.cleaned_data['ano']
        mes = self.form.cleaned_data['mes']

        hoje = datetime.date.today()
        if ano is None:
            ano_atual = hoje.year
        else:
            ano_atual = ano
        if mes is None:
            mes_atual = hoje.month
        else:
            mes_atual = mes

        self.context.update({
            'ano': ano_atual,
            'mes': mes_atual,
        })

        # ignorando form
        dia_atual = hoje.day
        dias_mes = dias_mes_data(hoje)

        nat_oper=(1, 2)
        self.context.update({
            'nat_oper': nat_oper,
        })

        pedidos = l_q_p.pedido_faturavel_modelo(
            cursor, periodo=f'-{dia_atual}:{dias_mes-dia_atual}', nat_oper=nat_oper)

        if len(pedidos) == 0:
            self.context.update({
                'msg_erro': 'Nenhum pedido encontrado',
            })
            return

        total_pedido = 0
        for pedido in pedidos:
            total_pedido += pedido['PRECO']
            pedido['DATA'] = pedido['DATA'].date()
        # total_pedido = int(round(total_pedido/1000))

        totalize_data(pedidos, {
            'sum': ['QTD', 'PRECO'],
            'descr': {'cliente': 'Total:'},
            'row_style': 'font-weight: bold;',
        })

        self.context.update({
            'headers': ['Pedido', 'Data', 'Cliente',
                        'Referência', 'Quantidade', 'Valor', 'Situação'],
            'fields': ['PEDIDO', 'DATA', 'CLIENTE',
                        'REF', 'QTD', 'PRECO', 'FAT'],
            'data': pedidos,
            'style': {
                5: 'text-align: right;',
                6: 'text-align: right;',
            },
        })
