import re
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from base.views import O2BaseGetPostView

import insumo.queries as queries
import insumo.forms as forms


class MapaComprasNecessidades(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(MapaComprasNecessidades, self).__init__(*args, **kwargs)
        self.Form_class = forms.MapaComprasNecessidadesForm
        self.template_name = 'insumo/mapa_compras_necessidades.html'
        self.title_name = 'Necessidade (mapa)'
        self.get_args = ['nivel', 'ref', 'tamanho', 'cor']

    def mount_context(self):
        nivel = self.form.cleaned_data['nivel']
        ref = self.form.cleaned_data['ref']
        tamanho = self.form.cleaned_data['tamanho']
        cor = self.form.cleaned_data['cor']

        if ref == '':
            return
        self.context.update({
            'nivel': nivel,
            'ref': ref,
            'tamanho': tamanho,
            'cor': cor,
        })

        cursor = connections['so'].cursor()

        data = queries.mapa_compras_necessidades(
            cursor, nivel, ref, cor, tamanho)

        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma necessidade de insumos encontrada',
            })
            return self.context

        self.context.update({
            'headers': ('Semana', 'Quantidade'),
            'fields': ('SEMANA_NECESSIDADE', 'QTD_INSUMO'),
            'data': data,
        })

        return self.context
