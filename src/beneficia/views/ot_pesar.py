from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.functions.views import (
    cleanned_fields_to_context,
    context_to_form_post,
)

from beneficia import forms
from beneficia import queries


class OtPesar(View):

    Form_class = forms.ot_pesar.OtPesarForm
    template_name = 'beneficia/ot_pesar.html'
    title_name = 'Insumos a pesar'

    cleanned_fields_to_context = cleanned_fields_to_context
    context_to_form_post = context_to_form_post

    def __init__(self):
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        dados, per, dtini, dtfim = queries.ot_pesar.query(
            self.cursor,
            periodo=self.context['periodo'],
            data=self.context['data'],
        )
        if len(dados) == 0:
            return

        self.context.update({
            'headers': [
                'OT',
                'Período',
                'OP',
                'Item',
                'Peso previsto',
                'Peso real',
            ],
            'fields': [
                'ot',
                'per',
                'op',
                'item',
                'p_previsto',
                'p_real',
            ],
            'dados': dados,
            'per': per,
            'dtini': dtini,
            'dtfim': dtfim,
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