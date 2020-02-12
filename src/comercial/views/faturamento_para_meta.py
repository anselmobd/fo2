from pprint import pprint
import datetime

from django.db import connections
from django.shortcuts import render
from django.views import View

from base.views import O2BaseGetPostView
from utils.functions import dias_mes_data
from utils.models import queryset_to_dict_list_lower
from utils.views import totalize_data

import lotes.queries.pedido as l_q_p
import comercial.forms
import comercial.models
import comercial.queries


class FaturamentoParaMeta(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(FaturamentoParaMeta, self).__init__(*args, **kwargs)
        self.Form_class = comercial.forms.FaturamentoParaMetaForm
        self.template_name = 'comercial/faturamento_para_meta.html'
        self.title_name = 'Faturamento para meta'

    def mount_context(self):
        cursor = connections['so'].cursor()

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

        faturados = comercial.queries.faturamento_para_meta(
            cursor, ano_atual, mes_atual, tipo='detalhe')

        totalize_data(faturados, {
            'sum': ['valor'],
            'descr': {'data': 'Total:'},
            'row_style': 'font-weight: bold;',
        })

        for faturado in faturados:
            faturado['valor|DECIMALS'] = 2

        self.context.update({
            'headers': ['Nota', 'Data', 'Cliente', 'Valor', ],
            'fields': ['nf', 'data', 'cliente', 'valor', ],
            'data': faturados,
            'style': {
                4: 'text-align: right;',
            },
        })
