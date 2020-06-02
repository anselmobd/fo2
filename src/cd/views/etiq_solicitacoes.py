from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
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


class EtiquetasSolicitacoes(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_inventorize_lote'
        self.Form_class = cd.forms.EtiquetasSolicitacoesForm
        self.template_name = 'cd/etiq_solicitacoes.html'
        self.context = {
            'titulo': 'Etiquetas de solicitações',
            'passo': 1,
        }

    def mount_context(self, request, form):
        cursor = connection.cursor()

        numero = form.cleaned_data['numero']
        buscado_numero = form.cleaned_data['buscado_numero']
        impresso_numero = form.cleaned_data['impresso_numero']

        self.context.update({
            'numero': numero,
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
            form.data['numero'] = ''
            self.context.update({
                'msg': 'Impressão marcada como confirmada',
                'passo': 1,
            })

        else:  # request.POST.get("busca"):
            form.data['buscado_numero'] = numero
            self.context.update({
                'passo': 2,
            })

    def get(self, request, *args, **kwargs):
        form = self.Form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        mutable_request_post = request.POST.copy()
        form = self.Form_class(mutable_request_post)
        if form.is_valid():
            self.mount_context(request, form)
        self.context['form'] = form
        return render(request, self.template_name, self.context)
