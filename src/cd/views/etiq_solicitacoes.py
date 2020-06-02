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
        self.context = {
            'titulo': self.title_name,
            'passo': 1,
        }

    def mount_context(self, request, form):
        cursor = connection.cursor()

        numero = form.cleaned_data['numero']

        self.context.update({
            'numero': numero,
            # por padrão, se chegou aqui é porque fez uma
            # busca (passo 1) válida
            'passo': 2,
        })

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

        for row in data:
            row['lote__lote|LINK'] = reverse(
                'producao:posicao__get',
                args=[row['lote__lote']])
            row['lote__lote|TARGET'] = '_BLANK'

        self.context.update({
            'headers': [
                'Endereço', 'OP', 'Lote',
                'Referência', 'Cor', 'Tamanho',
                'Quant. original', 'Quant. Solicitada'
            ],
            'fields': [
                'lote__local', 'lote__op', 'lote__lote',
                'lote__referencia', 'lote__cor', 'lote__tamanho',
                'lote__qtd_produzir', 'qtdsum'
            ],
            'data': data,
        })

        pprint(request.POST)
        if request.POST.get("volta_para_busca"):
            self.context.update({
                'passo': 1,
            })

        elif request.POST.get("volta_para_imprime"):
            self.context.update({
                'passo': 2,
            })

        elif request.POST.get("imprime"):
            self.context.update({
                'msg': 'Enviado para a impressora',
                'passo': 3,
            })

        elif request.POST.get("confirma"):
            # form.data['numero'] = ''  # não sei porque não está permitindo
            self.context.update({
                'msg': 'Impressão marcada como confirmada',
                'passo': 1,
            })

    def get(self, request, *args, **kwargs):
        form = self.Form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.Form_class(request.POST)
        if form.is_valid():
            self.mount_context(request, form)
        self.context['form'] = form
        return render(request, self.template_name, self.context)
