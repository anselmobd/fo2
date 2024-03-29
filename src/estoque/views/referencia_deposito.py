from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from o2.functions.iterable import get_defa
import utils.functions.strings
from utils.views import group_rowspan, totalize_grouped_data

from produto.queries.get_modelos import list_modelos_query

from estoque import forms
from estoque.queries.referencia_deposito import *


class ReferenciaDeposito(View):

    def __init__(self, *args, **kwargs):
        super(ReferenciaDeposito).__init__(*args, **kwargs)
        self.Form_class = forms.ReferenciasEstoqueForm
        self.template_name = 'estoque/referencia_deposito.html'
        self.context = {
            'titulo': 'Em depósito',
            'str_depositos': self.str_depositos(),
        }

    def mount_context(
            self, request, cursor, deposito, modelo, filtra_qtd, tipo_prod):
        context = {
            'deposito': deposito,
            'modelo': str(modelo) if modelo else '',
            'filtra_qtd': filtra_qtd,
            'tipo_prod': tipo_prod,
        }

        modelos = list_modelos_query(cursor)
        if modelo:
            try:
                modelo_idx = modelos.index(modelo)
            except ValueError:
                context.update({'erro': 'Modelo inexistente'})
                return context

            context.update({
                'anterior': get_defa(modelos, modelo_idx-1),
                'posterior': get_defa(modelos, modelo_idx+1),
            })

        dados = referencia_deposito_query(
            cursor, modelo, todos=(filtra_qtd == 't'), deposito=deposito, tipo_ref=tipo_prod)

        if not dados:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in dados:
            row['dep|TARGET'] = '_blank'
            row['dep|LINK'] = reverse(
                'estoque:mostra_estoque__get', args=[
                    row['dep'], '-', modelo])
            row['ref|TARGET'] = '_blank'
            row['ref|LINK'] = reverse(
                'estoque:mostra_estoque__get', args=[
                    row['dep'], row['ref']])

        group = ['dep']
        tot_conf = {
            'group': group,
            'sum': ['estoque', 'falta', 'soma'],
            'descr': {'ref': 'Totais:'},
        }
        if deposito == 'A00':
            tot_conf.update({
                'global_sum': ['estoque', 'falta', 'soma'],
                'global_descr': {'ref': 'Totais gerais:'},
            })
        totalize_grouped_data(dados, tot_conf)
        group_rowspan(dados, group)

        context.update({
            'headers': ['Depósito', 'Referência', 'Estoque positivo',
                        'Estoque negativo', 'Soma'],
            'fields': ['dep', 'ref', 'estoque',
                       'falta', 'soma'],
            'group': group,
            'data': dados,
            'style': {
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
            },
        })

        return context

    def str_depositos(seft):
        texto = utils.functions.strings.join2(
            (', ', ' e '), (101, 102, 103, 122, 231))
        return texto

    def get(self, request, *args, **kwargs):
        cursor = db_cursor_so(request)
        form = self.Form_class(cursor=cursor)
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        cursor = db_cursor_so(request)
        form = self.Form_class(request.POST, cursor=cursor)
        if form.is_valid():
            deposito = form.cleaned_data['deposito']
            modelo = form.cleaned_data['modelo']
            filtra_qtd = form.cleaned_data['filtra_qtd']
            tipo_prod = form.cleaned_data['tipo_prod']
            self.context.update(self.mount_context(
                request, cursor, deposito, modelo, filtra_qtd, tipo_prod))
        self.context['form'] = form
        return render(request, self.template_name, self.context)
