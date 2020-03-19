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

    def mount_context(self, request, cursor, ref, tam, cor, deposito):
        context = {}

        if len(ref) == 0:
            context.update({'erro': 'Digite algo em Referência'})
            return context

        context.update({
            'nivel': 1,
            'tam': tam,
            'cor': cor,
            'deposito': deposito,
            'botao': botao,
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
            ref = form.cleaned_data['ref']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            deposito = form.cleaned_data['deposito']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                request, cursor, ref, tam, cor, deposito))
        context['form'] = form
        return render(request, self.template_name, context)
