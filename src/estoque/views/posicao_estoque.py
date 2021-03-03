from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_data

from estoque import forms, queries


class PosicaoEstoque(View):
    Form_class = forms.PorDepositoForm
    template_name = 'estoque/posicao_estoque.html'
    title_name = 'Posição de estoque'

    def mount_context(
            self, cursor, nivel, ref, tam, cor, deposito, agrupamento, tipo):
        context = {
            'nivel': nivel,
            'tam': tam,
            'cor': cor,
            'deposito': deposito,
            'agrupamento': agrupamento,
            'tipo': tipo,
            }
        modelo = None
        if len(ref) % 5 == 0:
            context.update({
                'ref': ref,
            })
        else:
            modelo = ref.lstrip("0")
            ref = ''
            context.update({
                'modelo': modelo,
            })
        data = queries.posicao_estoque(
            cursor, nivel, ref, tam, cor, deposito, zerados=False,
            group=agrupamento, tipo=tipo, modelo=modelo)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        if agrupamento == 'r':
            totalize_data(data, {
                'sum': ['qtd_positiva', 'qtd_negativa'],
                'count': [],
                'descr': {'dep_descr': 'Totais:'},
                'row_style': 'font-weight: bold;',
            })
            soma = data[-1]['qtd_positiva'] + data[-1]['qtd_negativa']
            context.update({
                'headers': ('Nível', 'Referência', 'Depósito',
                            'Quantidades Positivas', 'Quantidades Negativas'),
                'fields': ('cditem_nivel99', 'cditem_grupo', 'dep_descr',
                           'qtd_positiva', 'qtd_negativa'),
                'style': {4: 'text-align: right;',
                          5: 'text-align: right;'},
                'soma': soma,
            })
        elif agrupamento == 'd':
            totalize_data(data, {
                'sum': ['qtd_positiva', 'qtd_negativa'],
                'count': [],
                'descr': {'dep_descr': 'Totais:'},
                'row_style': 'font-weight: bold;',
            })
            soma = data[-1]['qtd_positiva'] + data[-1]['qtd_negativa']
            context.update({
                'headers': ('Depósito',
                            'Quantidades Positivas', 'Quantidades Negativas'),
                'fields': ('dep_descr',
                           'qtd_positiva', 'qtd_negativa'),
                'style': {2: 'text-align: right;',
                          3: 'text-align: right;'},
                'soma': soma,
            })
        elif agrupamento == 'tc':
            totalize_data(data, {
                'sum': ['qtd_positiva', 'qtd_negativa'],
                'count': [],
                'descr': {'cditem_item': 'Totais:'},
                'row_style': 'font-weight: bold;',
            })
            soma = data[-1]['qtd_positiva'] + data[-1]['qtd_negativa']
            context.update({
                'headers': ('Nível', 'Tamanho', 'Cor',
                            'Quantidades Positivas', 'Quantidades Negativas'),
                'fields': ('cditem_nivel99', 'cditem_subgrupo', 'cditem_item',
                           'qtd_positiva', 'qtd_negativa'),
                'style': {4: 'text-align: right;',
                          5: 'text-align: right;'},
                'soma': soma,
            })
        elif agrupamento == 'ct':
            totalize_data(data, {
                'sum': ['qtd_positiva', 'qtd_negativa'],
                'count': [],
                'descr': {'cditem_item': 'Totais:'},
                'row_style': 'font-weight: bold;',
            })
            soma = data[-1]['qtd_positiva'] + data[-1]['qtd_negativa']
            context.update({
                'headers': ('Nível', 'Cor', 'Tamanho',
                            'Quantidades Positivas', 'Quantidades Negativas'),
                'fields': ('cditem_nivel99', 'cditem_item', 'cditem_subgrupo',
                           'qtd_positiva', 'qtd_negativa'),
                'style': {4: 'text-align: right;',
                          5: 'text-align: right;'},
                'soma': soma,
            })
        elif agrupamento == 'rctd':
            totalize_data(data, {
                'sum': ['qtd'],
                'count': [],
                'descr': {'dep_descr': 'Total:'},
                'row_style': 'font-weight: bold;',
            })
            context.update({
                'headers': ('Nível', 'Referência', 'Cor',
                            'Tamanho', 'Depósito', 'Quantidade'),
                'fields': ('cditem_nivel99', 'cditem_grupo', 'cditem_item',
                           'cditem_subgrupo', 'dep_descr', 'qtd'),
                'style': {6: 'text-align: right;'},
            })
        else:  # rtcd
            totalize_data(data, {
                'sum': ['qtd'],
                'count': [],
                'descr': {'dep_descr': 'Total:'},
                'row_style': 'font-weight: bold;',
            })
            lote_acomp_0 = True
            for row in data:
                if row['lote_acomp'] != 0:
                    lote_acomp_0 = False
            if lote_acomp_0:
                context.update({
                    'headers': ('Nível', 'Referência',
                                'Tamanho', 'Cor',
                                'Depósito', 'Quantidade'),
                    'fields': ('cditem_nivel99', 'cditem_grupo',
                               'cditem_subgrupo', 'cditem_item',
                               'dep_descr', 'qtd'),
                })
            else:
                context.update({
                    'headers': ('Nível', 'Referência',
                                'Tamanho', 'Cor', 'Depósito',
                                'Lote do produto', 'Quantidade'),
                    'fields': ('cditem_nivel99', 'cditem_grupo',
                               'cditem_subgrupo', 'cditem_item', 'dep_descr',
                               'lote_acomp', 'qtd'),
                    'style': {7: 'text-align: right;'},
                })
            data[-1]['lote_acomp'] = ''
            context.update({
                'style': {7: 'text-align: right;'},
            })
        context.update({
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        cursor = db_cursor_so(request)
        context = {'titulo': self.title_name}
        form = self.Form_class(cursor=cursor)
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        cursor = db_cursor_so(request)
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST, cursor=cursor)
        if form.is_valid():
            nivel = form.cleaned_data['nivel']
            ref = form.cleaned_data['ref']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            deposito = form.cleaned_data['deposito']
            agrupamento = form.cleaned_data['agrupamento']
            tipo = form.cleaned_data['tipo']
            context.update(self.mount_context(
                cursor, nivel, ref, tam, cor, deposito, agrupamento, tipo))
        context['form'] = form
        return render(request, self.template_name, context)
