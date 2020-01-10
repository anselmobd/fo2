from django.db import connections
from django.shortcuts import render
from django.views import View

from estoque import forms
from estoque import queries


class EstoqueNaData(View):

    def __init__(self):
        self.Form_class = forms.EstoqueNaDataForm
        self.template_name = 'estoque/estoque_na_data.html'
        self.title_name = 'Estoque na data'

    def mount_context(self, cursor, data, hora, deposito):
        context = {
            'data': data,
            'hora': hora,
            'deposito': deposito,
            }

        data = queries.estoque_na_data(cursor, data, hora, deposito)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data['data']
            hora = form.cleaned_data['hora']
            deposito = form.cleaned_data['deposito']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, data, hora, deposito))
        context['form'] = form
        return render(request, self.template_name, context)
