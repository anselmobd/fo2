from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View

from geral.functions import has_permission
from utils.functions.views import cleanned_fields_to_context

from estoque import forms
from estoque import queries


class Transferencia(View):

    Form_class = forms.TransferenciaForm
    template_name = 'estoque/transferencia.html'
    title_name = 'Transferência entre depósitos'

    cleanned_fields_to_context = cleanned_fields_to_context

    def __init__(self):
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        cursor = connections['so'].cursor()

        if self.context['ref'] == 0:
            self.context.update({'erro': 'Digite algo em Referência'})
            return

        return

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            self.context['form'] = self.Form_class(self.context)
            self.mount_context()
        return render(request, self.template_name, self.context)
