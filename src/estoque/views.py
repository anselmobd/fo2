from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View

from utils.views import totalize_data, totalize_grouped_data

from . import forms
from . import models


def index(request):
    context = {}
    return render(request, 'estoque/index.html', context)


class PorDeposito(View):
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
        if agrupamento == 'rct':
            group = ''
        else:
            group = agrupamento
        data = models.posicao_estoque(
            cursor, nivel, ref, tam, cor, deposito, zerados=False, group=group,
            tipo=tipo, modelo=modelo)
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
        else:
            totalize_data(data, {
                'sum': ['qtd'],
                'count': [],
                'descr': {'dep_descr': 'Total:'},
                'row_style': 'font-weight: bold;',
            })
            context.update({
                'headers': ('Nível', 'Referência', 'Tamanho',
                            'Cor', 'Depósito', 'Quantidade'),
                'fields': ('cditem_nivel99', 'cditem_grupo', 'cditem_subgrupo',
                           'cditem_item', 'dep_descr', 'qtd'),
                'style': {6: 'text-align: right;'},
            })
        context.update({
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            nivel = form.cleaned_data['nivel']
            ref = form.cleaned_data['ref']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            deposito = form.cleaned_data['deposito']
            agrupamento = form.cleaned_data['agrupamento']
            tipo = form.cleaned_data['tipo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, nivel, ref, tam, cor, deposito, agrupamento, tipo))
        context['form'] = form
        return render(request, self.template_name, context)


class ValorMp(View):
    Form_class = forms.ValorForm
    template_name = 'estoque/valor_mp.html'
    title_name = 'Valor de estoque'

    def mount_context(
            self, cursor, nivel, positivos, zerados, negativos, preco_zerado,
            deposito_compras):
        context = {
            'nivel': nivel,
            'positivos': positivos,
            'zerados': zerados,
            'negativos': negativos,
            'preco_zerado': preco_zerado,
            'deposito_compras': deposito_compras,
        }

        data = models.valor(
            cursor, nivel, positivos, zerados, negativos, preco_zerado,
            deposito_compras)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        totalize_grouped_data(data, {
            'group': ['nivel'],
            'sum': ['total'],
            'count': [],
            'descr': {'deposito': 'Total:'}
        })

        for row in data:
            row['qtd|DECIMALS'] = 2
            row['preco|DECIMALS'] = 2
            row['total|DECIMALS'] = 2

        context.update({
            'headers': ('Nível', 'Referência', 'Tamanho', 'Cor',
                        'Conta estoque', 'Depósito',
                        'Quantidade', 'Preço', 'Total'),
            'fields': ('nivel', 'ref', 'tam', 'cor',
                       'conta_estoque', 'deposito',
                       'qtd', 'preco', 'total'),
            'style': {
                7: 'text-align: right;',
                8: 'text-align: right;',
                9: 'text-align: right;',
            },
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            nivel = form.cleaned_data['nivel']
            positivos = form.cleaned_data['positivos']
            zerados = form.cleaned_data['zerados']
            negativos = form.cleaned_data['negativos']
            preco_zerado = form.cleaned_data['preco_zerado']
            deposito_compras = form.cleaned_data['deposito_compras']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, nivel, positivos, zerados, negativos, preco_zerado,
                deposito_compras))
        context['form'] = form
        return render(request, self.template_name, context)


class InventarioExpedicao(View):
    Form_class = forms.InventarioExpedicaoForm
    template_name = 'estoque/inventario_expedicao.html'
    title_name = 'Inventário p/ expedição'

    def mount_context(self, cursor, data_ini):
        context = {
            'data_ini': data_ini,
        }

        refs = models.refs_com_movimento(cursor, data_ini)
        if len(refs) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        deps = [231, 101, 102]
        for ref in refs:
            ref['deps'] = []
            for dep in deps:
                header, fields, data, style, total = \
                    models.grade_estoque(
                        cursor, ref['ref'], dep, data_ini=data_ini)
                grade = None
                if total != 0:
                    grade = {
                        'headers': header,
                        'fields': fields,
                        'data': data,
                        'style': style,
                    }
                    ref['deps'].append({
                        'dep': dep,
                        'grade': grade,
                    })

        context.update({
            'headers': ['Referência'],
            'fields': ['ref'],
            'refs': refs,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            data_ini = form.cleaned_data['data_ini']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, data_ini))
        context['form'] = form
        return render(request, self.template_name, context)


class ReferenciasEstoque(View):
    Form_class = forms.ReferenciasEstoqueForm
    template_name = 'estoque/referencias_estoque.html'
    title_name = 'Referencias com estoque'

    def mount_context(self, cursor, tipo, modelo):
        context = {
            'tipo': tipo,
            'modelo': modelo,
        }

        refs = models.referencias_estoque(cursor, tipo, modelo)
        if len(refs) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        context.update({
            'headers': ['Referência'],
            'fields': ['ref'],
            'refs': refs,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            tipo = 'v'  # form.cleaned_data['tipo']
            modelo = form.cleaned_data['modelo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, tipo, modelo))
        context['form'] = form
        return render(request, self.template_name, context)
