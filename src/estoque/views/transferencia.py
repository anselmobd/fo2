from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View

from geral.functions import has_permission
from utils.functions.views import cleanned_fields_to_context

from estoque import forms
from estoque import queries


class Transfere():

    def __init__(
            self, cursor, nivel, ref, tam, cor, qtd,
            deposito_origem, deposito_destino):
        self.cursor = cursor
        self.nivel = nivel
        self.ref = ref
        self.tam = tam
        self.cor = cor
        self.qtd = qtd
        self.deposito_origem = deposito_origem
        self.deposito_destino = deposito_destino

        self.initial_vars()
        self.valid_entries()
        self.calc_vars()

    def initial_vars(self):
        self.item = f'{self.nivel}.{self.ref}.{self.tam}.{self.cor}'

    def calc_vars(self):
        self.estoque_origem = self.get_estoque(self.deposito_origem)
        self.estoque_destino = self.get_estoque(self.deposito_destino)
        self.novo_estoque_origem = self.estoque_origem - self.qtd
        self.novo_estoque_destino = self.estoque_destino + self.qtd

    def valid_entries(self):
        self.valid_item()
        self.valid_deps()

    def valid_item(self):
        produto = queries.get_preco_medio_niv_ref_cor_tam(
            self.cursor, self.nivel, self.ref, self.cor, self.tam)
        if len(produto) == 0:
            raise ValueError(f'Item {self.item} não encontrado.')

    def valid_deps(self):
        if self.deposito_origem == self.deposito_destino:
            raise ValueError('Depósitos devem ser diferentes')

    def get_estoque(self, deposito_field):
        l_estoque = queries.get_estoque_dep_niv_ref_cor_tam(
            self.cursor, deposito_field,
            self.nivel, self.ref, self.cor, self.tam)
        if len(l_estoque) == 0:
            return 0
        else:
            return l_estoque[0]['estoque']

    def exec(self):
        pass


class Transferencia(View):

    Form_class = forms.TransferenciaForm
    template_name = 'estoque/transferencia.html'
    title_name = 'Transferência entre depósitos'

    cleanned_fields_to_context = cleanned_fields_to_context

    def __init__(self):
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = connections['so'].cursor()

        try:
            transf = Transfere(
                self.cursor,
                *(self.context[f] for f in [
                    'nivel', 'ref', 'tam', 'cor', 'qtd',
                    'deposito_origem', 'deposito_destino'])
            )
        except Exception as e:
            self.context.update({
                'erro': f'Transferência inválida ({e}).'
            })
            return

        self.context.update({
            'estoque_origem': transf.estoque_origem,
            'estoque_destino': transf.estoque_destino,
            'novo_estoque_origem': transf.novo_estoque_origem,
            'novo_estoque_destino': transf.novo_estoque_destino,
        })

        if 'executa' in self.request.POST:
            try:
                transf.exec()
            except Exception as e:
                self.context.update({
                    'erro_exec': e,
                })
                return
            self.context.update({
                'sucesso': 'Transferência executada.'
            })

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            self.context['form'] = self.Form_class(self.context)
            self.request = request
            self.mount_context()
        return render(request, self.template_name, self.context)
