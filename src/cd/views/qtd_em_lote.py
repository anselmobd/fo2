from pprint import pprint

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from lotes.models.inventario import InventarioLote
from lotes.queries.lote import get_lote
from lotes.views.lote.conserto_lote import dict_conserto_lote

import cd.forms
import cd.views.gerais
from cd.queries.endereco import (
    lotes_em_local,
    esvazia_palete,
    get_palete,
    palete_guarda_hist,
)
from cd.queries.inventario_lote import get_qtd_lotes_63


class QtdEmLote(LoginRequiredMixin, View):

    def __init__(self):
        self.Form_class = cd.forms.QtdEmLoteForm
        self.template_name = 'cd/qtd_em_lote.html'
        self.context = {'titulo': 'Qtd. em lote'}

    def zera(self, sufixo=''):
        self.context['form'].data[f'quant{sufixo}'] = None
        self.context['form'].data[f'lote{sufixo}'] = None

    def zera_conf(self):
        self.zera('_conf')

    def grava_inventario_lote(self, usuario, lote, quantidade, dados_lote):
        try:
            invent = InventarioLote()
            invent.lote = lote
            invent.quantidade = quantidade
            invent.usuario = usuario
            invent.save()
            return None
        except Exception as e:
            return e

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        quant_conf = self.context['form'].cleaned_data['quant_conf']
        lote_conf = self.context['form'].cleaned_data['lote_conf']
        quant = self.context['form'].cleaned_data['quant']
        lote = self.context['form'].cleaned_data['lote']

        self.context['identificado'] = False
        self.zera()

        # dados_lote = get_lote.query(cursor, lote)
        dados_lote = get_qtd_lotes_63(cursor, lote)
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

        erro_exec = self.grava_inventario_lote(
            self.request.user, lote, quant, dados_lote)
        if erro_exec:
            self.context.update({
                'erro': f"Problenas ao gravar dados <{erro_exec}>."})
        else:
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
        self.request = request
        self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.context['form'].data = self.context['form'].data.copy()
            self.mount_context()
        return render(request, self.template_name, self.context)
