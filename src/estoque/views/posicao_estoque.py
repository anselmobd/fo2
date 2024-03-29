import re
from pprint import pprint

from django.views import View
from django.urls import reverse

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from o2.views.base.get_post import O2BaseGetPostView
from geral.functions import has_permission
from utils.table_defs import TableDefs
from utils.views import totalize_data, get_total_row

from estoque import forms, queries


class PosicaoEstoque(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        self._cursor = None
        super(PosicaoEstoque, self).__init__(*args, **kwargs)
        self.Form_class = forms.PorDepositoForm
        self.template_name = 'estoque/posicao_estoque.html'
        self.title_name = 'Posição de estoque'
        self.cleaned_data2self = True

        self.por_pagina = 50
        self.table = TableDefs(
            {
                'nivel': ['Nível'],
                'ref': ['Referência'],
                'cor': [],
                'tam': ['Tamanho'],
                'modelo': ['Modelo'],
                'dep_descr': ['Depósito'],
                'lote_acomp': ['Lote do produto'],
                'qtd_positiva': ['Quant. Positiva', 'r'],
                'qtd_negativa': ['Quant. Negativa', 'r'],
                'qtd': ['Quantidade', 'r', 0],
                'zera': [
                    (
                        ('<span id="span_zera_tudo" '
                         'class="glyphicon glyphicon-minus-sign">'
                         '</span>'),
                    ),
                    'c'
                ],
                'item_no_tempo': ['No tempo', 'c'],
            },
            ['header', '+style', 'decimals'],
            style = {
                'r': 'text-align: right;',
                'c': 'text-align: center;',
            }
        )
        self.agrup_fields = {
            'rd': (
                'nivel', 'ref', 'dep_descr',
                'qtd_positiva', 'qtd_negativa',  'qtd'
            ),
            'md': (
                'nivel', 'modelo', 'dep_descr',
                'qtd_positiva', 'qtd_negativa',  'qtd'
            ),
            'r': (
                'nivel', 'ref',
                'qtd_positiva', 'qtd_negativa',  'qtd'
            ),
            'm': (
                'nivel', 'modelo',
                'qtd_positiva', 'qtd_negativa',  'qtd'
            ),
            'd': (
                'dep_descr',
                'qtd_positiva', 'qtd_negativa',  'qtd'
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

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = db_cursor_so(self.request)
        return self._cursor

    def pre_form(self):
        self.form_create_kwargs = {'cursor': self.cursor}

    def totalize_data(self, data, sum, descr, get=False):
        tot_func = get_total_row if get else totalize_data
        return tot_func(data, {
            'sum': sum,
            'descr': descr,
            'row_style': 'font-weight: bold;',
        })


    def totalizers(self, data, sum_text, get=False):
        if self.agrupamento in ['rd', 'md', 'd']:
            return self.totalize_data(
                data,
                ['qtd_positiva', 'qtd_negativa', 'qtd'],
                {'dep_descr': sum_text},
                get=get,
            )
        elif self.agrupamento in ['r']:
            return self.totalize_data(
                data,
                ['qtd_positiva', 'qtd_negativa', 'qtd'],
                {'ref': sum_text},
                get=get,
            )
        elif self.agrupamento in ['m']:
            return self.totalize_data(
                data,
                ['qtd_positiva', 'qtd_negativa', 'qtd'],
                {'modelo': sum_text},
                get=get,
            )
        elif self.agrupamento in ['tc', 'ct']:
            return self.totalize_data(
                data,
                ['qtd_positiva', 'qtd_negativa', 'qtd'],
                {'cor': sum_text},
                get=get,
            )
        elif self.agrupamento in ['rctd', 'rtcd', 'rtcd+']:
            return self.totalize_data(
                data,
                ['qtd'],
                {'dep_descr': sum_text},
                get=get,
            )

    def mount_context(self):
        self.modelo = None

        if any([ch in self.ref for ch in ' ,-']):
            filtro_refs = [
                filtro
                for filtro in re.split(r'[\s,-]', self.ref)
                if filtro
            ]
            self.ref = []
            self.modelo = []
            for filtro in filtro_refs:
                if len(filtro) % 5 != 0:
                    self.modelo.append(filtro.lstrip("0"))
                else:
                    self.ref.append(filtro)
        else:
            if len(self.ref) % 5 != 0:
                self.modelo = self.ref.lstrip("0")
                self.ref = ''

        data = queries.posicao_estoque(
            self.cursor, self.nivel, self.ref, self.tam, self.cor,
            self.deposito, zerados=False, group=self.agrupamento,
            tipo=self.tipo, modelo=self.modelo, empresa=1)

        if not data:
            return

        if self.agrupamento == 'rtcd':
            for row in data:
                if row['lote_acomp'] != 0:
                    self.agrupamento = 'rtcd+'
                    break

        row_totalizer = self.totalizers(data, 'Totais gerais:', get=True)

        data = paginator_basic(data, self.por_pagina, self.page)

        if data.paginator.num_pages > 1:
            self.totalizers(data.object_list, 'Totais da página:')

        if row_totalizer:
            data.object_list.append(row_totalizer)

        self.table.cols(
            *self.agrup_fields[self.agrupamento]
        )

        if self.agrupamento == 'rd':
            if has_permission(
                self.request,
                'estoque.pode_zerar_depositos'
            ):
                self.table.add('zera')
                for row in data.object_list:
                    if row['nivel']:
                        row['zera|SAFE'] = True
                        row['zera'] = (
                            '<span class="zera" id="zera_{ref}_{deposito}">-</span>'.format(
                                **row))
                    else:
                        row['zera'] = ' '

        elif self.agrupamento in ['rctd', 'rtcd', 'rtcd+']:
            self.table.add('item_no_tempo')
            for row in data.object_list:
                row['item_no_tempo'] = ''
                if row['nivel']:
                    row['item_no_tempo|GLYPHICON'] = 'glyphicon-time'
                    row['item_no_tempo|TARGET'] = '_BLANK'
                    row['item_no_tempo|LINK'] = reverse(
                        'estoque:item_no_tempo__get', args=[
                            row['ref'], row['cor'], row['tam'], row['deposito']])

        headers, fields, style, decimals = self.table.hfsd()

        self.context.update({
            'headers': headers,
            'fields': fields,
            'style': style,
            'decimals': decimals,
            'data': data,
        })
