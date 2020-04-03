from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connections
from django.shortcuts import render
from django.views import View

from utils.functions.views import cleanned_fields_to_context

from estoque import classes
from estoque import forms
from estoque import models


class Transferencia(PermissionRequiredMixin, View):

    Form_class = forms.TransferenciaForm
    template_name = 'estoque/transferencia.html'
    title_name = 'Movimentações'

    cleanned_fields_to_context = cleanned_fields_to_context

    def __init__(self):
        self.permission_required = 'estoque.can_transferencia'
        self.context = {'titulo': self.title_name}

    def valid_tipo(self):
        try:
            tip_mov = models.TipoMovStq.objects.get(codigo=self.kwargs['tipo'])
        except models.TipoMovStq.DoesNotExist as e:
            self.context.update({
                'erro_input': True,
                'erro_msg':
                    f'Tipo de movimento de estoque "{self.kwargs["tipo"]}" '
                    'não cadastrado.',
            })
            return
        return tip_mov

    def get_tipo(self):
        self.tip_mov = self.valid_tipo()
        if self.tip_mov:
            self.context.update({
                'titulo': self.tip_mov.descricao,
            })

    def mount_context(self):
        self.cursor = connections['so'].cursor()

        try:
            transf = classes.Transfere(
                self.cursor, self.tip_mov,
                *(self.context[f] for f in [
                    'nivel', 'ref', 'tam', 'cor', 'qtd',
                    'deposito_origem', 'deposito_destino',
                    'num_doc', 'descricao']),
                self.request,
                cria_num_doc=('executa' in self.request.POST)
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
            'num_doc': transf.num_doc,
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
                'sucesso_msg': f"{self.context['titulo']} executada."
            })

    def get(self, request, *args, **kwargs):
        self.get_tipo()
        self.context['form'] = self.Form_class(user=request.user)
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.get_tipo()
        self.context['form'] = self.Form_class(
            request.POST, user=self.request.user)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            if self.tip_mov:
                self.mount_context()
            self.context['form'] = self.Form_class(
                self.context, user=self.request.user)
        return render(request, self.template_name, self.context)
