from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.functions.views import (
    cleanned_fields_to_context,
    context_to_form_post,
    )

import produto.functions as pro_fun

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
            'tipo_mov__descricao',
            'item__produto__nivel',
            'item__produto__referencia',
            'item__cor__cor',
            'item__tamanho__tamanho__nome',
            'quantidade',
            'deposito_origem',
            'deposito_destino',
            'novo_item__produto__nivel',
            'novo_item__produto__referencia',
            'novo_item__cor__cor',
            'novo_item__tamanho__tamanho__nome',
            'usuario__username',
            'hora',
        ]
        dados = dados.values(*fields)

        for row in dados:
            row['str_item'] = pro_fun.item_str(
                row['item__produto__nivel'],
                row['item__produto__referencia'],
                row['item__tamanho__tamanho__nome']
                row['item__cor__cor'],
            )

            if row['novo_item__produto__nivel'] is None:
                row['str_novo_item'] = '='
            else:
                row['str_novo_item'] = pro_fun.item_str(
                    row['novo_item__produto__nivel'],
                    row['novo_item__produto__referencia'],
                    row['novo_item__tamanho__tamanho__nome']
                    row['novo_item__cor__cor'],
                )

            if row['deposito_origem'] == 0:
                row['deposito_origem'] = '-'
            else:
                row['deposito_origem|GLYPHICON'] = 'glyphicon-time'
                row['deposito_origem|TARGET'] = '_BLANK'
                row['deposito_origem|LINK'] = reverse(
                    'estoque:item_no_tempo__get', args=[
                        row['item__produto__referencia'],
                        row['item__cor__cor'],
                        row['item__tamanho__tamanho__nome'],
                        row['deposito_origem']])

            if row['deposito_destino'] == 0:
                row['deposito_destino'] = '-'
            else:
                row['deposito_destino|GLYPHICON'] = 'glyphicon-time'
                row['deposito_destino|TARGET'] = '_BLANK'
                row['deposito_destino|LINK'] = reverse(
                    'estoque:item_no_tempo__get', args=[
                        row['novo_item__produto__referencia'],
                        row['novo_item__cor__cor'],
                        row['novo_item__tamanho__tamanho__nome'],
                        row['deposito_destino']])

        headers = [
            'Tipo de Movimento',
            'Item',
            'Quantidade',
            'Dep. origem',
            'Dep. destino',
            'Novo item',
            'Usuário',
            'Hora',
        ]
        fields = [
            'tipo_mov__descricao',
            'str_item',
            'quantidade',
            'deposito_origem',
            'deposito_destino',
            'str_novo_item',
            'usuario__username',
            'hora',
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
