from operator import itemgetter
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from utils.functions.dictlist import filter_dictlist_to_grade_qtd

from cd.queries.novo_modulo.lotes import lotes_em_estoque


class GradeEstoqueTotais(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'cd.can_view_grades_estoque'
        self.template_name = 'cd/novo_modulo/grade_estoque_totais.html'

    def grade_dados(self, dados, referencia):
        return filter_dictlist_to_grade_qtd(
                dados,
                field_filter='ref',
                facade_filter='referencia',
                value_filter=referencia,
                field_linha='cor',
                field_coluna='tam',
                facade_coluna='Tamanho',
                field_ordem_coluna='ordem_tam',
                field_quantidade='qtd',
            )

    def mount_context(self):
        filtra_ref = '>B0000'
        referencias = lotes_em_estoque(self.cursor, get='ref', ref=filtra_ref)

        referencias = sorted(referencias, key=itemgetter('modelo', 'ref'))

        referencias = paginator_basic(referencias, 9999, self.page)

        inventario = lotes_em_estoque(self.cursor, tipo='i', ref=filtra_ref)
        pedido = lotes_em_estoque(self.cursor, tipo='p', ref=filtra_ref)
        solicitado = lotes_em_estoque(self.cursor, tipo='s', ref=filtra_ref)

        grades = []
        modelo_ant = -1
        for row_ref in referencias.object_list:
            referencia = row_ref['ref']
            modelo = row_ref['modelo']

            grade_invent_ref = self.grade_dados(inventario, referencia)
            grade_pedido_ref = self.grade_dados(pedido, referencia)
            grade_solicitado_ref = self.grade_dados(solicitado, referencia)

            grade_ref = {
                'inventario': grade_invent_ref,
                'pedido': grade_pedido_ref,
                'solicitacoes': grade_solicitado_ref,
                'solped_titulo': 'Pedidos',
                'ref': referencia,
                'refnum': modelo,
            }

            if modelo_ant != modelo:
                grade_ref.update({
                    'refnum': modelo,
                })
                modelo_ant = modelo

            grades.append(grade_ref)
            # break

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
