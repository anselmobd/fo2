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
from utils.functions.dictlist import dados_to_grade

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
