from pprint import pprint

from django.db import connections
from django.shortcuts import render
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

        for row in dados:
            row['maq'] = f"{row['grup_maq']} {row['sub_maq']} {row['num_maq']:05}"
            if row['dt_canc'] is None:
                row['canc'] = '-'
            else:
                row['canc'] = f"{row['cod_canc']:03} {row['dt_canc'].date()}"

        self.context.update({
            'headers': ('Cancelamento', 'Período', 'Equipamento', 'OT'),
            'fields': ('canc', 'periodo', 'maq', 'ot'),
            'dados': dados,
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
