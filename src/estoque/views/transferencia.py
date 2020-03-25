from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View

from utils.functions.views import cleanned_fields_to_context

from estoque import forms
from estoque import functions


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
            transf = functions.Transfere(
                self.cursor,
                *(self.context[f] for f in [
                    'nivel', 'ref', 'tam', 'cor', 'qtd',
                    'deposito_origem', 'deposito_destino'])
            )
        except Exception as e:
            self.context.update({
                'erro_input': True,
                'erro_msg': e,
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
                    'erro_exec': True,
                    'erro_msg': e,
                })
                return
            self.context.update({
                'sucesso_msg': 'Transferência executada.'
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
