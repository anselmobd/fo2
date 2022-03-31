from pprint import pprint

from django.views import View
from django.urls import reverse

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView
from geral.functions import has_permission
from utils.views import totalize_data, TableDefs

from estoque import forms, queries


class PosicaoEstoque(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        self._cursor = None
        super(PosicaoEstoque, self).__init__(*args, **kwargs)
        self.Form_class = forms.PorDepositoForm
        self.template_name = 'estoque/posicao_estoque.html'
        self.title_name = 'Posição de estoque'
        self.cleaned_data2self = True

        self.table = TableDefs(
            {
                'nivel': ['Nível'],
                'ref': ['Referência'],
                'cor': [],
                'tam': ['Tamanho'],
                'dep_descr': ['Depósito'],
                'lote_acomp': ['Lote do produto'],
                'qtd_positiva': ['Quant. Positiva', 'r'],
                'qtd_negativa': ['Quant. Negativa', 'r'],
                'qtd': ['Quantidade', 'r', 0],
                'zera': [('<span id="span_zera_tudo">Zera</span>', ), 'c'],
                'item_no_tempo': ['No tempo', 'c'],
            },
            ['header', '+style', 'decimals'],
            style = {
                'r': 'text-align: right;',
                'c': 'text-align: center;',
            }
        )
        self.agrup_fields = {
            'r': (
                'nivel', 'ref', 'dep_descr',
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

    def totalize_data(self, data, sum, descr):
        totalize_data(data, {
            'sum': sum,
            'descr': descr,
            'row_style': 'font-weight: bold;',
        })

    def totalizers(self, data, sum_text):
        if self.agrupamento in ['r', 'd']:
            self.totalize_data(
                data,
                ['qtd_positiva', 'qtd_negativa', 'qtd'],
                {'dep_descr': sum_text},
            )
        elif self.agrupamento in ['tc', 'ct']:
            self.totalize_data(
                data,
                ['qtd_positiva', 'qtd_negativa', 'qtd'],
                {'cor': sum_text},
            )
        elif self.agrupamento in ['rctd', 'rtcd']:
            self.totalize_data(
                data,
                ['qtd'],
                {'dep_descr': sum_text},
            )

    def mount_context(self):
        self.modelo = None
        if len(self.ref) % 5 != 0:
            self.modelo = self.ref.lstrip("0")
            self.ref = ''

        data = queries.posicao_estoque(
            self.cursor, self.nivel, self.ref, self.tam, self.cor,
            self.deposito, zerados=False, group=self.agrupamento,
            tipo=self.tipo, modelo=self.modelo)

        if not data:
            return

        self.totalizers(data, 'Totais gerais:')

        agrup = self.agrupamento
        if self.agrupamento == 'rtcd':
            for row in data:
                if row['lote_acomp'] != 0:
                    agrup = 'rtcd+'
                    break

        row_totalizer = data[-1].copy()

        data = paginator_basic(data, 50, self.page)

        if data.paginator.num_pages > 1:
            if len(data.object_list) > 2:
                if self.page == data.paginator.num_pages:
                    data.object_list = data.object_list[:-1]

                self.totalizers(data.object_list, 'Totais da página:')

                data.object_list.append(row_totalizer)

        self.table.cols(
            *self.agrup_fields[agrup]
        )

        if self.agrupamento == 'r':
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
