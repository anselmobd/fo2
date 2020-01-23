from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.forms import *

import rh.queries


class CriaUsuario(View):

    def __init__(self):
        self.Form_class = CriaUsuarioForm
        self.template_name = 'cria_usuario.html'
        self.context = {'titulo': 'Criar usuário'}

    def mount_context(self):
        cursor = connections['so'].cursor()
        pcursor = connections['persona'].cursor()

        if 'busca' in self.context:
            data = rh.queries.trabalhadores(
                pcursor,
                **{f: self.context[f] for f in ['codigo']})
            if len(data) != 1:
                self.context.update({
                    'erro': 'Trabalhador com esse código não encontrado',
                })
                return
            pprint(data)
            self.context.update({
                'trabalhador': data[0],
            })

    def cleanned_fields_to_context(self, post):
        for field in self.context['form'].fields:
            self.context[field] = self.context['form'].cleaned_data[field]
        for field in post:
            if field not in self.context:
                self.context[field] = post[field]

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context(request.POST)
            self.context['form'] = self.Form_class(self.context)
            self.mount_context()
        return render(request, self.template_name, self.context)
