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

        if ano is None or mes is None:
            hoje = datetime.date.today()
            ano_atual = hoje.year
            mes_atual = hoje.month
        else:
            ano_atual = ano
            mes_atual = mes

        self.context.update({
            'ano': ano_atual,
            'mes': mes_atual,
        })

        faturados = comercial.queries.devolucao_para_meta(
            cursor, ano_atual, mes_atual)

        if len(faturados) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma devolução encontrada',
            })
            return

        totalize_data(faturados, {
            'sum': ['qtd', 'valor'],
            'descr': {'cliente': 'Total:'},
            'row_style': 'font-weight: bold;',
        })

        self.context.update({
            'headers': ['Nota', 'Data', 'CFOP', 'Cliente',
                        'Referência', 'Quantidade', 'Valor', ],
            'fields': ['nf', 'data', 'cfop', 'cliente',
                        'ref', 'qtd', 'valor', ],
            'data': faturados,
            'style': {
                6: 'text-align: right;',
                7: 'text-align: right;',
            },
        })
