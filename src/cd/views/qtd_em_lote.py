from pprint import pprint

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

import lotes.models
import lotes.queries
from lotes.queries.lote.get_lotes import get_lote
from lotes.views.lote.conserto_lote import dict_conserto_lote

import cd.forms
import cd.views.gerais
from cd.queries.endereco import (
    lotes_em_local,
    esvazia_palete,
    get_palete,
    palete_guarda_hist,
)


class QtdEmLote(View):

    def __init__(self):
        self.Form_class = cd.forms.QtdEmLoteForm
        self.template_name = 'cd/qtd_em_lote.html'
        self.context = {'titulo': 'Qtd. em lote'}

    def zera(self, sufixo=''):
        self.context['form'].data[f'quant{sufixo}'] = None
        self.context['form'].data[f'lote{sufixo}'] = None

    def zera_conf(self):
        self.zera('_conf')

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        quant_conf = self.context['form'].cleaned_data['quant_conf']
        lote_conf = self.context['form'].cleaned_data['lote_conf']
        quant = self.context['form'].cleaned_data['quant']
        lote = self.context['form'].cleaned_data['lote']

        self.context['identificado'] = False
        self.zera()
        pprint([quant_conf, lote_conf, quant, lote])

        dados_lote = get_lote(cursor, lote)
        if not dados_lote:
            self.context.update({
                'erro': "Lote inexistênte."})
            return

        if not lote_conf:
            self.context['form'].data['quant_conf'] = quant
            self.context['form'].data['lote_conf'] = lote
            self.context['identificado'] = True
            return

        if lote_conf != lote:
            self.context.update({
                'erro': "Lote não confirmado."})
            self.zera_conf()
            return

        if quant_conf != quant:
            self.context.update({
                'erro': "Quantidade não confirmada."})
            self.zera_conf()
            return

        grava_qtd_em_lote()
        self.context.update({
            'confirmado': True,
            'lote': lote,
            'quant': quant,
        })
        self.zera_conf()

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        request = self.request
        self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.context['form'].data = self.context['form'].data.copy()
            self.mount_context()
        return render(request, self.template_name, self.context)


def grava_qtd_em_lote():
    pass