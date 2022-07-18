from pprint import pprint

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connection
from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.classes import TermalPrint

import lotes.models

from cd.forms import etqs_parciais
from cd.queries import novo_modulo


class EtiquetasParciais(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_print__solicitacao_parciais'
        self.Form_class = etqs_parciais.EtiquetasParciaisForm
        self.template_name = 'cd/etqs_parciais.html'
        self.context = {'titulo': 'Etiquetas de parciais'}

    def imprime(self, data):
        impresso_slug = 'etiqueta-de-parciais'
        try:
            impresso = lotes.models.Impresso.objects.get(
                slug=impresso_slug)
        except lotes.models.Impresso.DoesNotExist:
            self.context.update({
                'msg': f"Impresso '{impresso_slug}' não cadastrado.",
            })
            return False

        try:
            usuario_impresso = lotes.models.UsuarioImpresso.objects.get(
                usuario=self.request.user, impresso=impresso)
        except lotes.models.UsuarioImpresso.DoesNotExist:
            self.context.update({
                'msg': f"Impresso '{impresso_slug}' não cadastrado para o usuário '{self.request.user}'.",
            })
            return False

        teg = TermalPrint(
            usuario_impresso.impressora_termica.nome,
                file_dir="impresso/solicitacao/%Y/%m"
        )
        teg.template(usuario_impresso.modelo.gabarito, '\r\n')
        teg.printer_start()
        try:
            for row in data:
                teg.context(row)
                teg.printer_send()
        finally:
            teg.printer_end()

        return True

    def seleciona(self, data, selecao):
        intervals = [
            v.strip()
            for v in selecao.split(',')
            if v.strip() not in ('', '-')
        ]

        if len(intervals) == 0:
            return data

        selecionadas = set()
        for interval in intervals:
            limits = [i.strip() for i in interval.split('-')]
            ini = limits[0]
            try:
                fim = limits[1]
            except Exception:
                fim = ini
            ini = int(ini) if ini != '' else 1
            fim = int(fim) if fim != '' else len(data)
            for num in range(ini, fim+1):
                selecionadas.add(num)
        return [d for n, d in enumerate(data) if n+1 in selecionadas]

    def mount_context(self, form):
        cursor = db_cursor_so(self.request)

        numero = form.cleaned_data['numero']
        buscado_numero = form.cleaned_data['buscado_numero']
        selecao = form.cleaned_data['selecao']

        if self.request.POST.get("imprime"):
            if buscado_numero != numero:
                form.data['numero'] = ''
                form.add_error(
                    'numero', "Número a imprimir deve ser previamente buscado"
                )
                return

        form.data['buscado_numero'] = numero

        self.context.update({
            'numero': numero,
        })

        solicitacao = novo_modulo.solicitacao.get_solicitacao(
            cursor,
            solicitacao=numero,
        )

        data = [
            row
            for row in solicitacao
            if row['qtd_ori'] != row['qtde']
        ]

        for n, row in enumerate(data):
            row['n'] = n + 1

        self.context.update({
            'headers': [
                "Nº", "Palete", "Endereço", "OP", "Lote",
                "Referência", "Cor", "Tamanho",
                "Quant. original", "Quant. Solicitada",
            ],
            'fields': [
                'n', 'palete', 'endereco', 'ordem_producao', 'lote',
                'ref', 'cor', 'tam',
                'qtd_ori', 'qtde',
            ],
            'data': data,
        })

        if self.request.POST.get("imprime"):
            data_selecao = []
            try:
                data_selecao = self.seleciona(data, selecao)
            except Exception as e:
                self.context.update({
                    'msg': "Seleção para impressão inválida",
                })
            pprint(data_selecao)

            if data_selecao:
                if self.imprime(data_selecao):
                    self.context.update({
                        'msg': "Enviado para a impressora",
                    })
            else:
                self.context.update({
                    'msg': "Nada selecionado",
                })

            return

    def get(self, request, *args, **kwargs):
        self.request = request
        form = self.Form_class(request=request)
        self.context['form'] = form
        return render(self.request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        mutable_request_post = self.request.POST.copy()
        form = self.Form_class(mutable_request_post, request=request)
        if form.is_valid():
            self.mount_context(form)
        self.context['form'] = form
        return render(self.request, self.template_name, self.context)
