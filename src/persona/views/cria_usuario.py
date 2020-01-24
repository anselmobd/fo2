import datetime
import time
from pprint import pprint

from django import forms
from django.contrib.auth.models import User
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
            usuario = base.models.Colaborador.objects.get(
                matricula=self.context['codigo'])
            self.context.update({
                'erro': 'Usuário com essa matrícula já cadastrado como '
                        'colaborador',
                'login': usuario.user,
            })
            self.erro = True
            return
        except base.models.Colaborador.DoesNotExist:
            pass

        try:
            matricula_em_sobrenome = f"({self.context['codigo'].lstrip('0')})"
            print(matricula_em_sobrenome)
            usuario = User.objects.get(
                last_name__contains=matricula_em_sobrenome)
            self.context.update({
                'erro': 'Usuário com essa matrícula já cadastrado como '
                        'usuário',
                'login': usuario.username,
            })
            self.erro = True
            return
        except User.DoesNotExist:
            pass

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
            nomes = trabalhador['nome'].title().split()
            first_name = nomes[0]
            last_name = ' '.join(nomes[1:])
            password = (
                f"{self.context['cpf'][:4]}"
                f"{first_name[0].lower()}"
                f"{str(round(time.time() * 1000))[-3:]}"
                )
            usuario = User.objects.create_user(
                username=self.context['codigo'],
                first_name=first_name,
                last_name=last_name,
                password=password)

            self.context.update({
                'login': self.context['codigo'],
                'password': password,
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
