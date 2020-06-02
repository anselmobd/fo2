from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connections
from django.shortcuts import render
from django.views import View

import lotes.models

import cd.forms


class Rearrumar(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_inventorize_lote'
        self.Form_class = cd.forms.RearrumarForm
        self.template_name = 'cd/rearrumar.html'
        self.title_name = 'Rearrumar pallet na rua'

    def mount_context(self, request, form):
        cursor = connections['so'].cursor()
        context = {}

        rua = form.cleaned_data['rua'].upper()
        endereco = form.cleaned_data['endereco']
        valid_rua = form.cleaned_data['valid_rua']
        valid_endereco = form.cleaned_data['valid_endereco']

        if request.POST.get("confirma"):
            if rua != valid_rua:
                form.add_error(
                    'rua', "Rua não pode ser alterada na confirmação"
                )
            if endereco != valid_endereco:
                form.add_error(
                    'endereco', "Endereco não pode ser alterado na confirmação"
                )
            if not form.is_valid():
                return context

        data = lotes.models.Lote.objects.filter(
            local=endereco
        ).values(
            'op', 'lote', 'qtd_produzir',
            'referencia', 'cor', 'tamanho',
            'local_at', 'local_usuario__username'
        ).order_by('referencia', 'cor', 'ordem_tamanho', 'op', 'lote')

        q_lotes = len(data)
        q_itens = 0
        for row in data:
            q_itens += row['qtd_produzir']

        context.update({
            'q_lotes': q_lotes,
            'q_itens': q_itens,
            'headers': (
                'Referência', 'Tamanho', 'Cor', 'Quant',
                'OP', 'Lote', 'Em', 'Por'),
            'fields': (
                'referencia', 'tamanho', 'cor', 'qtd_produzir',
                'op', 'lote', 'local_at', 'local_usuario__username'),
            'data': data,
        })

        if request.POST.get("confirma"):
            lotes_recs = lotes.models.Lote.objects.filter(
                local=endereco)
            for lote in lotes_recs:
                lote.local = rua
                lote.local_usuario = request.user
                lote.save()

            form.data['endereco'] = ''

        else:  # request.POST.get("tira"):
            form.data['valid_rua'] = rua
            form.data['valid_endereco'] = endereco

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
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
