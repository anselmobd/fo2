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


class Ob(View):

    Form_class = beneficia.forms.ObForm
    template_name = 'beneficia/ob.html'
    title_name = 'OB'

    cleanned_fields_to_context = cleanned_fields_to_context
    context_to_form_post = context_to_form_post

    def __init__(self):
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = connections['so'].cursor()

        dados = beneficia.queries.busca_ob(self.cursor, self.context['ob'])
        if len(dados) == 0:
            return

        self.context.update({
            'headers': [
                'Período',
                'Equipamento',
                'Rolos',
                'Quilos',
                'Obs.',
                'Situação',
                'Cancelamento',
            ],
            'fields': [
                'periodo',
                'maq',
                'rolos',
                'quilos',
                'obs',
                'sit',
                'canc',
            ],
            'dados': dados,
        })

        est_dados = beneficia.queries.ob_estagios(self.cursor, self.context['ob'])
        self.context.update({
            'est_headers': (
                'Sequência',
                'Estágio',
                'Descrição',
                'Início',
                'Término',
            ),
            'est_fields': (
                'seq',
                'est',
                'est_descr',
                'ini',
                'fim',
            ),
            'est_dados': est_dados,
        })

        tec_dados = beneficia.queries.ob_tecidos(self.cursor, self.context['ob'])
        self.context.update({
            'tec_headers': [
                'Nível',
                'Ref,',
                'Tam.',
                'Cor',
                'Alt.',
                'Rot.',
                'Rolos prog.',
                'Quilos prog.',
                'Rolos real',
                'Quilos real',
                'Rolos prod.',
                'Quilos prod.',
            ],
            'tec_fields': [
                'nivel',
                'ref',
                'tam',
                'cor',
                'alt',
                'rot',
                'rolos_prog',
                'quilos_prog',
                'rolos_real',
                'quilos_real',
                'rolos_prod',
                'quilos_prod',
            ],
            'tec_dados': tec_dados,
        })

        tipo_tecido = ''
        for row in tec_dados:
            if not tipo_tecido:
                tipo_tecido = row['tam']
            elif tipo_tecido != row['tam']:
                tipo_tecido = 'X'

        tecido_ob = {
            'TIN': 'OB2',
            'INT': 'OB1',
            'X': 'Erro',
            '': 'Indefinido',
        }
        tipo_ob = tecido_ob[tipo_tecido]

        self.context.update({
            'tipo_ob': tipo_ob,
        })

        if tipo_ob == 'OB1':
            self.context['headers'].append('OB2')
            self.context['fields'].append('ob2')
        elif tipo_ob == 'OB2':
            self.context['headers'].append('OT')
            self.context['fields'].append('ot')

        dest_dados = beneficia.queries.ob_destinos(self.cursor, self.context['ob'])

        for row in dest_dados:
            if row['numero']:
                row['numero|LINK'] = reverse(
                    'beneficia:ob__get',
                    args=[row['numero']],
                )

        self.context.update({
            'dest_headers': [
                'Número',
                'Depósito',
                'Rolos',
                'Quilos',
            ],
            'dest_fields': [
                'numero',
                'dep',
                'rolos',
                'quilos',
            ],
            'dest_dados': dest_dados,
        })


    def get(self, request, *args, **kwargs):
        if 'ob' in kwargs:
            return self.post(request, *args, **kwargs)
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        if 'ob' in kwargs:
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
