from pprint import pprint

from django.db import connection
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.functions.digits import *

import lotes.models

import cd.queries as queries
import cd.forms


class EtiquetasSolicitacoes(View):

    def __init__(self):
        self.Form_class = cd.forms.EtiquetasSolicitacoesForm
        self.template_name = 'cd/etiq_solicitacoes.html'
        self.title_name = 'Etiquetas de solicitações'

    def mount_context(self, cursor, numero):
        context = {
            'numero': numero,
            }

        if not fo2_digit_valid(numero):
            context.update({'erro': 'Número inválido'})
            return context

        data = queries.historico(cursor, op)
        if len(data) == 0:
            context.update({'erro': 'Sem lotes ativos'})
            return context
        for row in data:
            if row['dt'] is None:
                row['dt'] = 'Nunca inventariado'
            if row['endereco'] is None:
                if row['usuario'] is None:
                    row['endereco'] = '-'
                else:
                    row['endereco'] = 'SAIU!'
            if row['usuario'] is None:
                row['usuario'] = '-'
        context.update({
            'headers': ('Data', 'Qtd. de lotes', 'Endereço', 'Usuário'),
            'fields': ('dt', 'qtd', 'endereco', 'usuario'),
            'data': data,
        })

        data = queries.historico_detalhe(cursor, op)
        for row in data:
            if row['dt'] is None:
                row['dt'] = 'Nunca inventariado'
            if row['endereco'] is None:
                if row['usuario'] is None:
                    row['endereco'] = '-'
                else:
                    row['endereco'] = 'SAIU!'
            if row['usuario'] is None:
                row['usuario'] = '-'
            row['lote|LINK'] = reverse(
                'cd:historico_lote', args=[row['lote']])
        context.update({
            'd_headers': ('Lote', 'Última data', 'Endereço', 'Usuário'),
            'd_fields': ('lote', 'dt', 'endereco', 'usuario'),
            'd_data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            numero = form.cleaned_data['numero']
            cursor = connection.cursor()
            context.update(self.mount_context(cursor, numero))
        context['form'] = form
        return render(request, self.template_name, context)
