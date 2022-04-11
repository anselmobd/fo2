from datetime import datetime
from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.functions import coalesce

import cd.forms
import cd.views.gerais
from cd.queries.endereco import (
    lotes_em_local,
    lotes_em_versao_palete,
)


class VisualizaEsvaziamento(View):

    def __init__(self):
        self.template_name = 'cd/vizualiza_esvaziamento.html'
        self.context = {'titulo': 'Esvaziamento'}

    def dtget_to_dt(self, data_versao):
        return datetime.strptime(data_versao, '%Y%m%d%H%M%S')

    def mount_context(self):
        palete = self.context['palete']
        data_versao = self.dtget_to_dt(
            self.context['data_versao'])
        self.context.update({
            'data_versao': data_versao,
        })

        lotes_versao = lotes_em_versao_palete(self.cursor, palete, data_versao)
        lotes_versao_dict = {
            row['lote']: row['data'].strftime('%d/%m/%y %H:%M:%S')
            for row in lotes_versao
        }

        lotes_end = lotes_em_local(self.cursor, palete)
        lotes_end_dict = {
            row['lote']: row['data'].strftime('%d/%m/%y %H:%M:%S')
            for row in lotes_end
        }

        lotes = set(lotes_versao_dict.keys())
        lotes = lotes.union(set(lotes_end_dict.keys()))

        dados = []
        for lote in sorted(lotes):
            data_antes = lotes_versao_dict[lote] if lote in lotes_versao_dict else None
            data_agora = lotes_end_dict[lote] if lote in lotes_end_dict else None
            if data_antes and not data_agora:
                style = 'color: red;'
            elif data_agora and not data_antes:
                style = 'color: darkorange;'
            else:
                style = 'color: darkgreen;'
            style += 'text-align: center;'
            dados.append({
                'lote': lote,
                'data_antes': coalesce(data_antes, 'inserido'),
                'data_agora': coalesce(data_agora, 'retirado'),
                '|STYLE': style,
            })

        self.context.update({
            'headers': ['Bipado antes', 'Lote', 'Bipado agora'],
            'fields': ['data_antes', 'lote', 'data_agora'],
            'data': dados,
        })

    def get(self, request, *args, **kwargs):
        self.cursor = db_cursor_so(request)
        self.context.update(kwargs)
        self.mount_context()
        return render(request, self.template_name, self.context)
