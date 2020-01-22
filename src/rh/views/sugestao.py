import datetime
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.views import totalize_data
from utils.functions import untuple_keys

import lotes.models
import lotes.queries.pedido

from estoque import forms
from estoque import queries
from estoque.functions import (
    transfo2_num_doc,
    transfo2_num_doc_dt,
    )


class Sugestao(View):

    def __init__(self):
        self.Form_class = forms.SugestaoForm
        self.template_name = 'rh/sugestao.html'
        self.context = {'titulo': 'Sugestão'}

    def mount_context(self):
        cursor = connections['so'].cursor()

    def cleanned_fields_to_context(self):
        for field in self.context['form'].fields:
            self.context[field] = self.context['form'].cleaned_data[field]

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            self.context['form'] = self.Form_class(self.context)
            self.mount_context()
        return render(request, self.template_name, self.context)
