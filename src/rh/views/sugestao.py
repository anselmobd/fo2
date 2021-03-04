from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from estoque import forms


class Sugestao(View):

    def __init__(self):
        self.Form_class = forms.SugestaoForm
        self.template_name = 'rh/sugestao.html'
        self.context = {'titulo': 'Sugestão'}

    def mount_context(self, cursor):
        pass

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
            cursor = db_cursor_so(request)
            self.mount_context(cursor)
        return render(request, self.template_name, self.context)
