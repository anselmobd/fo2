from pprint import pprint

from django import forms
from django.db import connections
from django.contrib.auth.mixins import PermissionRequiredMixin
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

            if form.is_valid():
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

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            self.mount_context(request, form)
        context['form'] = form
        return render(request, self.template_name, context)
