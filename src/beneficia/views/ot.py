from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_conn

from utils.functions.views import (
    cleanned_fields_to_context,
    context_to_form_post,
)

import beneficia.forms
import beneficia.queries


class Ot(View):

    Form_class = beneficia.forms.OtForm
    template_name = 'beneficia/ot.html'
    title_name = 'OT'

    cleanned_fields_to_context = cleanned_fields_to_context
    context_to_form_post = context_to_form_post

    def __init__(self):
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = db_conn('so', self.request).cursor()

        dados = beneficia.queries.busca_ot(self.cursor, self.context['ot'])
        if len(dados) == 0:
            return

        row = dados[0]
        if row['ob']:
            row['ob|LINK'] = reverse(
                'beneficia:ob__get',
                args=[row['ob']],
            )

        self.context.update({
            'headers': [
                'Tipo',
                'Máquina',
                'OB',
                'Situação',
                'Situação receita',
                'Relação Banho',
                'Volume Banho',
            ],
            'fields': [
                'tipo',
                'maq',
                'ob',
                'sit',
                'sit_receita',
                'relacao_banho',
                'volume_banho',
            ],
            'dados': dados,
        })


    def get(self, request, *args, **kwargs):
        if 'ot' in kwargs:
            return self.post(request, *args, **kwargs)
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        if 'ot' in kwargs:
            self.context['post'] = True
            self.context['form'] = self.Form_class(kwargs)
        else:
            self.context['post'] = 'busca' in self.request.POST
            self.context['form'] = self.Form_class(self.request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            self.mount_context()
            self.context_to_form_post()
            self.context['form'] = self.Form_class(self.context)
        return render(request, self.template_name, self.context)
