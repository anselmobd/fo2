from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View

from geral.functions import has_permission

from estoque import forms
from estoque import queries


class Transferencia(View):
    Form_class = forms.TransferenciaForm
    template_name = 'estoque/transferencia.html'
    title_name = 'Transferência entre depósitos'

    def mount_context(
            self, request, cursor, nivel, ref, tam, cor,
            deposito_origem, deposito_destino):
        context = {}

        if len(ref) == 0:
            context.update({'erro': 'Digite algo em Referência'})
            return context

        context.update({
            'nivel': nivel,
            'ref': ref,
            'tam': tam,
            'cor': cor,
            'deposito_origem': deposito_origem,
            'deposito_destino': deposito_destino,
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
            nivel = form.cleaned_data['nivel']
            ref = form.cleaned_data['ref']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            deposito_origem = form.cleaned_data['deposito_origem']
            deposito_destino = form.cleaned_data['deposito_destino']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                request, cursor, nivel, ref, tam, cor,
                deposito_origem, deposito_destino))
        context['form'] = form
        return render(request, self.template_name, context)
