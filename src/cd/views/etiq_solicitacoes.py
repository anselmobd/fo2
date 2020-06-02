from pprint import pprint

from django.db import connection
from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce
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

        solicitacao = lotes.models.SolicitaLote.objects.get(id=numero[:-2])

        data = lotes.models.SolicitaLoteQtd.objects.values(
            'lote__op', 'lote__lote', 'lote__qtd_produzir',
            'lote__referencia', 'lote__cor', 'lote__tamanho'
        ).annotate(
            lote_ordem=Coalesce('lote__local', Value('0000')),
            lote__local=Coalesce('lote__local', Value('-Ausente-')),
            qtdsum=Sum('qtd')
        ).filter(
            solicitacao=solicitacao,
        ).exclude(
            lote__qtd_produzir=F('qtdsum'),
        ).order_by(
            'lote_ordem', 'lote__op', 'lote__referencia', 'lote__cor',
            'lote__tamanho', 'lote__lote'
        )

        if len(data) == 0:
            context.update({'erro': 'Sem lotes parciais'})
            return context

        for row in data:
            if row['qtdsum'] == row['lote__qtd_produzir']:
                row['inteira_parcial'] = 'Lote inteiro'
            else:
                row['inteira_parcial'] = 'Parcial'
            row['lote__lote|LINK'] = reverse(
                'producao:posicao__get',
                args=[row['lote__lote']])
            row['lote__lote|TARGET'] = '_BLANK'

        context.update({
            'headers': [
                'Endereço', 'OP', 'Lote',
                'Referência', 'Cor', 'Tamanho',
                'Quant. original', 'Quant. Solicitada', 'Solicitação'
            ],
            'fields': [
                'lote__local', 'lote__op', 'lote__lote',
                'lote__referencia', 'lote__cor', 'lote__tamanho',
                'lote__qtd_produzir', 'qtdsum', 'inteira_parcial'
            ],
            'data': data,
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
