from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.functions import untuple_keys_concat
from utils.functions.strings import is_only_digits
from utils.functions.views import Fo2ViewMethods

from beneficia.forms.main import BuscaObForm
from beneficia.queries import busca_ob


class BuscaOb(View, Fo2ViewMethods):

    def __init__(self):
        super().__init__()
        self.Form_class = BuscaObForm
        self.template_name = 'beneficia/busca_ob.html'
        self.title_name = 'Busca OB'
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        dados = busca_ob.query(
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
            if is_only_digits(row['os']):
                row['os|TARGET'] = '_blank'
                row['os|LINK'] = reverse(
                    'producao:os__get', args=[row['os']])
            if is_only_digits(row['op']):
                row['op|TARGET'] = '_blank'
                row['op|LINK'] = reverse(
                    'producao:op__get', args=[row['op']])

        self.context.update({
            'headers': [
                'OB',
                'Período',
                'Equipamento',
                'Rolos',
                'Quilos',
                'Obs.',
                'OS',
                'OP',
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
                'os',
                'op',
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
