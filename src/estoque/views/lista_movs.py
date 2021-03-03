from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.functions.views import (cleanned_fields_to_context,
                                   context_to_form_post)

import produto.functions as pro_fun

from estoque import forms, models


class ListaMovimentos(View):

    Form_class = forms.ListaMovimentosForm
    template_name = 'estoque/lista_movs.html'
    title_name = 'Movimentações de um documento'

    cleanned_fields_to_context = cleanned_fields_to_context
    context_to_form_post = context_to_form_post

    def __init__(self):
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

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
            'tipo_mov__renomeia',
            'tipo_mov__unidade',
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
            'itens_extras',
        ]
        dados = dados.values(*fields)

        br = '<br />'
        for row in dados:
            row['str_item'] = pro_fun.item_str(
                row['item__produto__nivel'],
                row['item__produto__referencia'],
                row['item__tamanho__tamanho__nome'],
                row['item__cor__cor'],
            )
            if row['tipo_mov__unidade'] == 'M':
                row['str_item'] += br + row['itens_extras']

            if row['novo_item__produto__nivel'] is None:
                row['str_novo_item'] = '='
            else:
                row['str_novo_item'] = pro_fun.item_str(
                    row['novo_item__produto__nivel'],
                    row['novo_item__produto__referencia'],
                    row['novo_item__tamanho__tamanho__nome'],
                    row['novo_item__cor__cor'],
                )
            if row['tipo_mov__unidade'] == 'D':
                row['str_novo_item'] += br + row['itens_extras']


            if row['deposito_origem'] == 0:
                row['deposito_origem'] = '-'
            else:
                deposito = row['deposito_origem']
                link = reverse(
                    'estoque:item_no_tempo__get', args=[
                        row['item__produto__referencia'],
                        row['item__cor__cor'],
                        row['item__tamanho__tamanho__nome'],
                        deposito
                    ]
                )
                row['deposito_origem'] = f'''
                    <a href="{link}" target="_blank">{deposito}<span
                    class="glyphicon glyphicon-time" aria-hidden="true"></span></a>
                '''
                if row['tipo_mov__unidade'] == 'M':
                    for item in row['itens_extras'].split():
                        codes = item.split('.')
                        link = reverse(
                            'estoque:item_no_tempo__get', args=[
                                codes[1],
                                codes[3],
                                codes[2],
                                deposito
                            ]
                        )
                        row['deposito_origem'] += br + f'''
                            <a href="{link}" target="_blank">{deposito}<span
                            class="glyphicon glyphicon-time" aria-hidden="true"></span></a>
                        '''

            if row['deposito_destino'] == 0:
                row['deposito_destino'] = '-'
            else:
                row['deposito_destino|GLYPHICON'] = 'glyphicon-time'
                row['deposito_destino|TARGET'] = '_BLANK'
                if row['tipo_mov__renomeia']:
                    deposito = row['deposito_destino']
                    link = reverse(
                        'estoque:item_no_tempo__get', args=[
                            row['novo_item__produto__referencia'],
                            row['novo_item__cor__cor'],
                            row['novo_item__tamanho__tamanho__nome'],
                            deposito
                        ]
                    )
                    row['deposito_destino'] = f'''
                        <a href="{link}" target="_blank">{deposito}<span
                        class="glyphicon glyphicon-time" aria-hidden="true"></span></a>
                    '''
                    if row['tipo_mov__unidade'] == 'D':
                        for item in row['itens_extras'].split():
                            codes = item.split('.')
                            link = reverse(
                                'estoque:item_no_tempo__get', args=[
                                    codes[1],
                                    codes[3],
                                    codes[2],
                                    deposito
                                ]
                            )
                            row['deposito_destino'] += br + f'''
                                <a href="{link}" target="_blank">{deposito}<span
                                class="glyphicon glyphicon-time" aria-hidden="true"></span></a>
                            '''

                else:
                    deposito = row['deposito_destino']
                    link = reverse(
                        'estoque:item_no_tempo__get', args=[
                            row['item__produto__referencia'],
                            row['item__cor__cor'],
                            row['item__tamanho__tamanho__nome'],
                            deposito
                        ]
                    )
                    row['deposito_destino'] = f'''
                        <a href="{link}" target="_blank">{deposito}<span
                        class="glyphicon glyphicon-time" aria-hidden="true"></span></a>
                    '''

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
        safe = [
            'str_item',
            'deposito_origem',
            'deposito_destino',
            'str_novo_item',
        ]
        self.context.update({
            'headers': headers,
            'fields': fields,
            'dados': dados,
            'safe': safe,
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
