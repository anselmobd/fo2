from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_conn

from utils.functions import untuple_keys_concat
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
        self.cursor = db_conn('so', self.request).cursor()

        dados = beneficia.queries.busca_ob(
            self.cursor,
            periodo=self.context['periodo'],
            obs=self.context['obs'],
            ordens=self.context['ordens'],
            ot=self.context['ot'],
            ob2=self.context['ob2'],
            ref=self.context['ref'],
        )
        if len(dados) == 0:
            return

        for row in dados:
            if row['ob2']:
                row['ob2|LINK'] = reverse(
                    'beneficia:ob__get',
                    args=[row['ob2']],
                )
            else:
                row['ob2'] = '-'
            if not row['ot']:
                row['ot'] = '-'
            row['ob|LINK'] = reverse(
                'beneficia:ob__get',
                args=[row['ob']],
            )
            row['quilos|DECIMALS'] = 2

        self.context.update({
            'headers': [
                'OB',
                'Período',
                'Equipamento',
                'Rolos',
                'Quilos',
                'Obs.',
                'Situação',
                'Cancelamento',
                'Referência',
                'OB2',
                'OT',
            ],
            'fields': [
                'ob',
                'periodo',
                'maq',
                'rolos',
                'quilos',
                'obs',
                'sit',
                'canc',
                'ref',
                'ob2',
                'ot',
            ],
            'style': untuple_keys_concat({
                (4, 5): 'text-align: right;',
                (9, 10, 11): 'text-align: center;',
            }),
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
