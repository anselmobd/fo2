from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View

from geral.functions import has_permission
from utils.functions.views import cleanned_fields_to_context

from estoque import forms
from estoque import queries


class Transferencia(View):

    Form_class = forms.TransferenciaForm
    template_name = 'estoque/transferencia.html'
    title_name = 'Transferência entre depósitos'

    cleanned_fields_to_context = cleanned_fields_to_context

    def __init__(self):
        self.context = {'titulo': self.title_name}

    def get_estoque(self, deposito_field):
        l_estoque = queries.get_estoque_dep_niv_ref_cor_tam(
            self.cursor, *(self.context[f] for f in [
                deposito_field, 'nivel', 'ref', 'cor', 'tam']))
        if len(l_estoque) == 0:
            return 0
        else:
            return l_estoque[0]['estoque']

    def mount_context(self):
        self.cursor = connections['so'].cursor()

        produto = queries.get_preco_medio_niv_ref_cor_tam(
            self.cursor, *(self.context[f] for f in [
                'nivel', 'ref', 'cor', 'tam']))
        pprint(produto)
        if len(produto) == 0:
            self.context.update({'erro': 'Erro: Item não encontrado'})
            return

        self.context.update({'estoque_origem': self.get_estoque(
            'deposito_origem')})
        self.context.update({'estoque_destino': self.get_estoque(
            'deposito_destino')})

        return

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
