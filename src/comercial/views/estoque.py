from pprint import pprint
from datetime import datetime, timedelta

from django.shortcuts import render
from django.db import connections
from django.views import View

from base.views import O2BaseGetView
from utils.functions import dec_month, dec_months

import comercial.models as models


class EstoqueDesejado(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(EstoqueDesejado, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/estoque_desejado.html'
        self.title_name = 'Estoque desejado'

    def mount_context(self):
        self.context.update({
            'headers': (),
            'fields': (),
            'data': [],
        })


class Ponderacao(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Ponderacao, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/ponderacao.html'
        self.title_name = 'Ponderação a aplicar'

    def mount_context(self):
        nfs = list(models.ModeloPassadoPeriodo.objects.filter(
            modelo_id=1).order_by('ordem').values())
        if len(nfs) == 0:
            self.context.update({
                'msg_erro': 'Nenhum período definido',
            })
            return

        data = list(nfs)

        hoje = datetime.today()
        mes = dec_month(hoje, 1)
        for row in data:
            row['mes_fim'] = mes.strftime("%m/%Y")
            mes = dec_months(mes, row['meses']-1)
            row['mes_ini'] = mes.strftime("%m/%Y")
            mes = dec_month(mes)

        self.context.update({
            'headers': ('# meses', 'Mês inicial', 'Mês final', 'Peso'),
            'fields': ('meses', 'mes_ini', 'mes_fim', 'peso'),
            'data': data,
        })
