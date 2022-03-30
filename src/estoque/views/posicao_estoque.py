from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from utils.views import totalize_data, TableDefs

from estoque import forms, queries


class PosicaoEstoque(View):
    Form_class = forms.PorDepositoForm
    template_name = 'estoque/posicao_estoque.html'
    title_name = 'Posição de estoque'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = TableDefs(
            {
                'nivel': ['Nível'],
                'ref': ['Referência'],
                'cor': [],
                'tam': ['Tamanho'],
                'dep_descr': ['Depósito'],
                'lote_acomp': ['Lote do produto'],
                'qtd_positiva': ['Quantidades Positivas', 'r'],
                'qtd_negativa': ['Quantidades Negativas', 'r'],
                'qtd': ['Quantidade', 'r', 0],
            },
            ['header', '+style', 'decimals'],
            style = {
                'r': 'text-align: right;',
            }
        )
        self.agrup_fields = {
            'r': (
                'nivel', 'ref', 'dep_descr',
                'qtd_positiva', 'qtd_negativa',  'qtd'
            ),
            'd': (
                'dep_descr', 'qtd_positiva', 'qtd_negativa',  'qtd'
            ),
            'tc': (
                'nivel', 'tam', 'cor',
                'qtd_positiva', 'qtd_negativa',  'qtd'
            ),
            'ct': (
                'nivel', 'cor', 'tam',
                'qtd_positiva', 'qtd_negativa',  'qtd'
            ),
            'rctd': (
                'nivel', 'ref', 'cor', 'tam',
                'dep_descr', 'qtd'
            ),
            'rtcd': (
                'nivel', 'ref', 'tam', 'cor',
                'dep_descr', 'qtd'
            ),
            'rtcd+': (
                'nivel', 'ref', 'tam', 'cor',
                'dep_descr', 'lote_acomp', 'qtd'
            ),
        }



    def totalize_data(self, data, sum, descr):
        totalize_data(data, {
            'sum': sum,
            'descr': descr,
            'row_style': 'font-weight: bold;',
        })

    def totalizers(self, agrupamento, data, dep_descr):
        if agrupamento in ['r', 'd']:
            self.totalize_data(
                data,
                ['qtd_positiva', 'qtd_negativa', 'qtd'],
                {'dep_descr': dep_descr},
            )
        elif agrupamento in ['tc', 'ct']:
            self.totalize_data(
                data,
                ['qtd_positiva', 'qtd_negativa', 'qtd'],
                {'cor': dep_descr},
            )
        elif agrupamento in ['rctd', 'rtcd']:
            self.totalize_data(
                data,
                ['qtd'],
                {'dep_descr': dep_descr},
            )

    def mount_context(
            self, cursor, nivel, ref, tam, cor,
            deposito, agrupamento, tipo, page):
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

        if not data:
            return context

        self.totalizers(agrupamento, data, 'Totais gerais:')

        agrup = agrupamento
        if agrupamento == 'rtcd':
            for row in data:
                if row['lote_acomp'] != 0:
                    agrup = 'rtcd+'
                    break

        headers, fields, style, decimals = self.table.hfsd(
            *self.agrup_fields[agrup]
        )

        row_totalizer = data[-1].copy()

        data = paginator_basic(data, 50, page)

        if data.paginator.num_pages > 1:
            if len(data.object_list) > 2:
                if page == data.paginator.num_pages:
                    data.object_list = data.object_list[:-1]

                self.totalizers(agrupamento, data.object_list, 'Totais da página:')

                data.object_list.append(row_totalizer)

        context.update({
            'headers': headers,
            'fields': fields,
            'style': style,
            'decimals': decimals,
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
            page = form.cleaned_data['page']
            context.update(self.mount_context(
                cursor, nivel, ref, tam, cor,
                deposito, agrupamento, tipo, page))
        context['form'] = form
        return render(request, self.template_name, context)
