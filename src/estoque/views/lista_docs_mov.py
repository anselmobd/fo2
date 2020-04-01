from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View

from utils.functions.views import (
    cleanned_fields_to_context,
    context_to_form_post,
    )

from estoque import forms
from estoque import models


class ListaDocsMovimentacao(View):

    Form_class = forms.ListaDocsMovimentacaoForm
    template_name = 'estoque/lista_movs.html'
    title_name = 'Lista documentos de movimentações'

    cleanned_fields_to_context = cleanned_fields_to_context
    context_to_form_post = context_to_form_post

    def __init__(self):
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = connections['so'].cursor()

        dados = models.DocMovStq.objects
        if self.context['data']:
            dados = dados.filter(data=self.context['data'])

        fields = ['num_doc', 'descricao', 'data', 'usuario__username']
        dados = dados.values(*fields)
        pprint(dados)
        for row in dados:
            pprint(row)

        headers = ['Documento', 'Descrição', 'Data', 'Usuário']
        self.context.update({
            'headers': headers,
            'fields': fields,
            'dados': dados,
            })

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            self.mount_context()
            self.context_to_form_post()
            self.context['form'] = self.Form_class(self.context)
        return render(request, self.template_name, self.context)
