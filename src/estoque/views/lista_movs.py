from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.functions.views import (
    cleanned_fields_to_context,
    context_to_form_post,
    )

from estoque import forms
from estoque import models


class ListaMovimentos(View):

    Form_class = forms.ListaMovimentosForm
    template_name = 'estoque/lista_movs.html'
    title_name = 'Movimentações de um documento'

    cleanned_fields_to_context = cleanned_fields_to_context
    context_to_form_post = context_to_form_post

    def __init__(self):
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = connections['so'].cursor()

        try:
            documento = models.DocMovStq.objects.get(
                num_doc=self.context['num_doc'])
        except models.DocMovStq.DoesNotExist:
            self.context.update({
                'erro_msg': 'Documento não encontrado'
            })
            return

        self.context.update({
            'infos': {
                'Data': documento.data,
                'Descrição': documento.descricao,
                'Usuário': documento.usuario.username,
            }
        })

        dados = models.MovStq.objects.filter(
            documento=documento)
        if len(dados) == 0:
            self.context.update({
                'erro_msg': 'Nenhum movimento encontrado'
            })
            return

        fields = [
            'item__produto__nivel',
            'item__produto__referencia',
            'item__cor__cor',
            'item__tamanho__tamanho__nome',
            'quantidade',
            'deposito_origem',
            'deposito_destino',
            'usuario__username',
        ]
        dados = dados.values(*fields)

        for row in dados:
            row['deposito_origem|GLYPHICON'] = 'glyphicon-time'
            row['deposito_origem|TARGET'] = '_BLANK'
            row['deposito_origem|LINK'] = reverse(
                'estoque:item_no_tempo__get', args=[
                    row['item__produto__referencia'],
                    row['item__cor__cor'],
                    row['item__tamanho__tamanho__nome'],
                    row['deposito_origem']])
            row['deposito_destino|GLYPHICON'] = 'glyphicon-time'
            row['deposito_destino|TARGET'] = '_BLANK'
            row['deposito_destino|LINK'] = reverse(
                'estoque:item_no_tempo__get', args=[
                    row['item__produto__referencia'],
                    row['item__cor__cor'],
                    row['item__tamanho__tamanho__nome'],
                    row['deposito_destino']])

        headers = [
            'Nível',
            'Referência',
            'Cor',
            'Tamanho',
            'Quantidade',
            'Dep. origem',
            'Dep. destino',
            'Usuário',
        ]
        self.context.update({
            'headers': headers,
            'fields': fields,
            'dados': dados,
            })

    def get(self, request, *args, **kwargs):
        if 'num_doc' in kwargs:
            return self.post(request, *args, **kwargs)
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        if 'num_doc' in kwargs:
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
