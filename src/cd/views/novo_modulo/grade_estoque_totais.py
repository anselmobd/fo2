from operator import itemgetter
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.views import View
from django.urls import reverse

from fo2.connections import db_cursor_so

from utils.views import group_rowspan

from base.paginator import paginator_basic
from utils.functions.strings import only_digits

import cd.forms
from cd.queries.novo_modulo.lotes import lotes_em_estoque


class GradeEstoqueTotais(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'cd.can_view_grades_estoque'
        self.template_name = 'cd/novo_modulo/grade_estoque_totais.html'

    def mount_context(self):
        referencias = lotes_em_estoque(self.cursor, get='ref', ref=['B0001', 'B0002'])

        referencias = sorted(referencias, key=itemgetter('modelo', 'ref'))

        referencias = paginator_basic(referencias, 2, self.page)

        inventario = lotes_em_estoque(self.cursor, tipo='i', ref=['B0001', 'B0002'])
        pedido = lotes_em_estoque(self.cursor, tipo='p', ref=['B0001', 'B0002'])
        solicitado = lotes_em_estoque(self.cursor, tipo='s', ref=['B0001', 'B0002'])

        grades = []
        for row_ref in referencias.object_list:
            referencia = row_ref['ref']

            inventario_ref = list(
                filter(
                    lambda x: x['ref'] == referencia,
                    inventario,
                )
            )
            # pprint(inventario_ref)

            grade_invent_ref = dados_to_grade(
                inventario_ref,
                field_linha='cor',
                field_coluna='tam',
                facade_coluna='Tamanho',
                field_ordem_coluna='ordem_tam',
                field_quantidade='qtd',
            )

            grade_invent_ref.update({
                'referencia': referencia,
            })
            # pprint(grade_invent_ref)

            grade_ref = {
                'inventario': grade_invent_ref,
                'ref': referencia,
                'refnum': row_ref['modelo'],
            }
            grades.append(grade_ref)

        headers = ["Referência", "Modelo"]
        fields = ['ref', 'modelo']
        self.context.update({
            # 'headers': headers,
            # 'fields': fields,
            # 'data': referencias,
            'grades': grades,
        })
        pprint(self.context)

    def get(self, request, *args, **kwargs):
        self.cursor = db_cursor_so(request)
        self.page = request.GET.get('page', 1)
        self.context = {}
        self.mount_context()
        return render(request, self.template_name, self.context)


def dados_to_grade(
    dados,
    field_linha=None,
    facade_linha=None,
    field_coluna=None,
    facade_coluna=None,
    field_ordem_coluna=None,
    field_quantidade=None,
):
    total = 'Total'

    if facade_linha is None:
        facade_linha = field_linha.capitalize()

    if facade_coluna is None:
        facade_coluna = field_coluna.capitalize()

    if not field_ordem_coluna:
        field_ordem_coluna = field_coluna

    indices_linhas = sorted(list(set([
        row[field_linha]
        for row in dados
    ])))

    indices_colunas_ordem = sorted(
        list(set([
            (row[field_coluna], row[field_ordem_coluna])
            for row in dados
        ])),
        key=lambda x: x[1],
    )
    indices_colunas = [
        r[0]
        for r in indices_colunas_ordem
    ]

    fields = [field_linha] + indices_colunas + [total]

    facades_list = []
    if facade_linha:
        facades_list.append(facade_linha)
    if facade_coluna:
        facades_list.append(facade_coluna)
    if not facades_list:
        facades_list['']    
    facedes = ' / '.join(facades_list)

    headers = [facedes] + indices_colunas + [total]

    style = {}
    for i in range(len(indices_colunas)):
        style[i+2] ='text-align: right;'
    style[len(indices_colunas)+2] = 'text-align: right;font-weight: bold;'

    data = []
    total_rows = {
        field_linha: total,
        '|STYLE': 'font-weight: bold;',
    }
    for coluna in indices_colunas:
        total_rows[coluna] = 0
    total_rows[total] = 0
    for linha in indices_linhas:
        row = {field_linha: linha}
        total_row = 0
        for coluna in indices_colunas:
            quantidades = [
                row[field_quantidade]
                for row in dados
                if (
                    row[field_linha] == linha
                    and row[field_coluna] == coluna
                )
            ]
            quantidade = sum(quantidades)
            row[coluna] = quantidade
            total_row += quantidade
            total_rows[coluna] += quantidade
            total_rows[total] += quantidade
        row[total] = total_row
        data.append(row)
    data.append(total_rows)

    return {
        'indices_linhas': indices_linhas,
        'indices_colunas': indices_colunas,
        'facedes': facedes,
        'fields': fields,
        'headers': headers,
        'style': style,
        'data': data,
        'total': total_rows[total],
    }
