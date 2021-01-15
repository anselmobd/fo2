from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.functions.views import (
    cleanned_fields_to_context,
    context_to_form_post,
)

import beneficia.forms
import beneficia.queries


class BuscaOb(View):

    Form_class = beneficia.forms.BuscaObForm
    template_name = 'beneficia/busca_ob.html'
    title_name = 'Busca OB'

    cleanned_fields_to_context = cleanned_fields_to_context
    context_to_form_post = context_to_form_post

    def __init__(self):
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = connections['so'].cursor()

        dados = beneficia.queries.busca_ob(
            self.cursor,
            periodo=self.context['periodo'],
            obs=self.context['obs'],
            ot=self.context['ot'],
            ref=self.context['ref'],
        )
        if len(dados) == 0:
            return

        for row in dados:
            row['ob|LINK'] = reverse(
                'beneficia:ob__get',
                args=[row['ob']],
            )

        self.context.update({
            'headers': (
                'OB',
                'Período',
                'Equipamento',
                'Rolos',
                'Quilos',
                'Obs.',
                'Situação',
                'Cancelamento',
                'OT'
            ),
            'fields': (
                'ob',
                'periodo',
                'maq',
                'rolos',
                'quilos',
                'obs',
                'sit',
                'canc',
                'ot'
            ),
            'dados': dados,
        })

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.context['post'] = 'busca' in self.request.POST
        self.context['form'] = self.Form_class(self.request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            self.mount_context()
            self.context_to_form_post()
            self.context['form'] = self.Form_class(self.context)
        return render(request, self.template_name, self.context)
