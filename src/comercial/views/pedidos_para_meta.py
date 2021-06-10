import datetime
from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.functions import dias_mes_data
from utils.views import totalize_data

import lotes.queries.pedido as l_q_p


class PedidosParaMeta(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(PedidosParaMeta, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/pedidos_para_meta.html'
        self.title_name = 'Pedidos no mês'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        hoje = datetime.date.today()

        # ignorando form
        dia_atual = hoje.day
        dias_mes = dias_mes_data(hoje)

        nat_oper=(1, 2)
        self.context.update({
            'nat_oper': nat_oper,
        })

        pedidos = l_q_p.pedido_faturavel_modelo(
            cursor, periodo=f'-{dia_atual}:{dias_mes-dia_atual}',
            nat_oper=nat_oper, group='p')

        if len(pedidos) == 0:
            self.context.update({
                'msg_erro': 'Nenhum pedido encontrado',
            })
            return

        n = 1
        for row in pedidos:
            row['DATA'] = row['DATA'].date()
            row['PEDIDO|LINK'] = reverse(
                'producao:pedido__get',
                args=[row['PEDIDO']],
            )

            row['valor|DECIMALS'] = 2
            row['N'] = n
            n += 1

        totalize_data(pedidos, {
            'sum': ['QTD', 'PRECO'],
            'descr': {'cliente': 'Total:'},
            'row_style': 'font-weight: bold;',
        })

        self.context.update({
            'headers': ['#', 'Pedido', 'Data', 'Cliente',
                        'Quantidade', 'Valor', 'Situação'],
            'fields': ['N', 'PEDIDO', 'DATA', 'CLIENTE',
                        'QTD', 'PRECO', 'FAT'],
            'data': pedidos,
            'style': {
                5: 'text-align: right;',
                6: 'text-align: right;',
            },
        })
