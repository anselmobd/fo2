from pprint import pprint

from django import forms
from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

import base.models

import persona.forms
import persona.queries as queries


class CriaUsuario(View):

    def __init__(self):
        self.Form_class = persona.forms.CriaUsuarioForm
        self.template_name = 'persona/cria_usuario.html'
        self.context = {'titulo': 'Criar usuário'}

    def mount_context(self):
        self.erro = False
        self.sucesso = False
        cursor = connections['so'].cursor()
        pcursor = connections['persona'].cursor()

        try:
            base.models.Colaborador.objects.get(
                matricula=self.context['codigo'])
        except base.models.Colaborador.DoesNotExist:
            self.context.update({
                'erro': 'Usuário com essa matrícula já cadastrado',
            })
            self.erro = True
            return

        data = queries.trabalhadores(
            pcursor,
            **{f: self.context[f] for f in ['codigo']})
        if len(data) != 1:
            self.context.update({
                'erro': 'Trabalhador com esse código não encontrado',
            })
            self.erro = True
            return
        trabalhador = data[0]
        self.context.update({
            'trabalhador': trabalhador,
        })

        if 'verifica' in self.context:
            print('verifica')
            if trabalhador['cpf'] != self.context['cpf']:
                print('diferente')
                self.context.update({
                    'erro': 'CPF informado não compatível com o cadastrado.',
                })
                self.erro = True
                return
            else:
                print('igual')

        if 'cria' in self.context:
            self.context.update({
                'login': 'login',
            })
            self.sucesso = True

    def cleanned_fields_to_context(self, post):
        for field in self.context['form'].fields:
            self.context[field] = self.context['form'].cleaned_data[field]
        for field in post:
            if field not in self.context:
                self.context[field] = post[field]

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def show_hidden(self):
        zera_form = False
        hidden_form = False

        if self.erro:
            zera_form = True
            hidden_form = True

        if self.sucesso:
            zera_form = True
            hidden_form = True

        if zera_form:
            self.context['form'] = self.Form_class()
        if hidden_form:
            self.context['form'].fields['codigo'].widget = (
                forms.HiddenInput())

        if not self.erro and not self.sucesso:
            if 'busca' in self.context:
                self.context['form'].fields['codigo'].widget = (
                    forms.HiddenInput())
                self.context['form'].fields['cpf'].widget = forms.TextInput(
                    attrs={'type': 'number', 'autofocus': 'autofocus'})
            if 'verifica' in self.context:
                self.context['form'].fields['codigo'].widget = (
                    forms.HiddenInput())

    def post(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context(request.POST)
            self.context['form'] = self.Form_class(self.context)
            self.mount_context()
            self.show_hidden()
        return render(request, self.template_name, self.context)
