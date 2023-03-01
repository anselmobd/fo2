from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.functions.views import Fo2ViewMethods

from beneficia import forms
from beneficia import queries


class OtPesar(View, Fo2ViewMethods):

    def __init__(self):
        super().__init__()
        self.Form_class = forms.ot_pesar.OtPesarForm
        self.template_name = 'beneficia/ot_pesar.html'
        self.title_name = 'Insumos a pesar'
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        dados, per, dtini, dtfim = queries.ot_pesar.query(
            self.cursor,
            periodo=self.context['periodo'],
            data=self.context['data'],
            selecao=self.context['selecao'],
        )

        self.context.update({
            'per': per,
            'dtini': dtini,
            'dtfim': dtfim,
        })

        if len(dados) == 0:
            return

        self.context.update({
            'headers': [
                'OT',
                'OP',
                'Item',
                'Peso previsto',
                'Peso real',
                'Pesador',
                'Nome',
            ],
            'fields': [
                'ot',
                'op',
                'item',
                'p_previsto',
                'p_real',
                'cod_pesador',
                'nome_pesador',
            ],
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
