from pprint import pprint

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

        context = {
            'endereco': endereco,
            'rua': rua,
        }

        lotes_no_local = lotes.models.Lote.objects.filter(
            local=endereco).count()

        if lotes_no_local == 0:
            context['erro'] = \
                f'O endereço "{endereco}" está vazio.'
            return context

        if request.POST.get("confirma"):
            lotes_recs = lotes.models.Lote.objects.filter(
                local=endereco)
            for lote in lotes_recs:
                lote.local = rua
                lote.local_usuario = request.user
                lote.save()

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
