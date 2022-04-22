import copy
from operator import itemgetter
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from utils.classes import Perf
from utils.functions.dictlist import filter_dictlist_to_grade_qtd

from lotes.views.a_produzir import (
    soma_grades,
    subtrai_grades,
    update_gzerada,
)

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
        p = Perf(id='GradeEstoqueTotais', on=True)
        filtra_ref = None  # '>A0000'
        referencias = lotes_em_estoque(self.cursor, get='ref', ref=filtra_ref)
        p.prt('referencias')

        referencias = sorted(referencias, key=itemgetter('modelo', 'ref'))

        referencias = paginator_basic(referencias, 20, self.page)
        p.prt('paginator')

        inventario = lotes_em_estoque(self.cursor, tipo='i', ref=filtra_ref)
        p.prt('inventario')
        pedido = lotes_em_estoque(self.cursor, tipo='p', ref=filtra_ref)
        p.prt('pedido')
        solicitado = lotes_em_estoque(self.cursor, tipo='s', ref=filtra_ref)
        p.prt('solicitado')

        grades = []
        modelo_ant = -1
        for row_ref in referencias.object_list:
            referencia = row_ref['ref']
            modelo = row_ref['modelo']

            gzerada = None
    
            grade_invent_ref = self.grade_dados(inventario, referencia)
            gzerada = update_gzerada(gzerada, grade_invent_ref)
            p.prt(f"{referencia} grade_invent_ref")

            grade_pedido_ref = self.grade_dados(pedido, referencia)
            if grade_pedido_ref['total'] != 0:
                gzerada = update_gzerada(gzerada, grade_pedido_ref)
            p.prt(f"{referencia} grade_pedido_ref")

            grade_solicitado_ref = self.grade_dados(solicitado, referencia)
            if grade_solicitado_ref['total'] != 0:
                gzerada = update_gzerada(gzerada, grade_solicitado_ref)
            p.prt(f"{referencia} grade_solicitado_ref")

            grade_invent_ref = soma_grades(gzerada, grade_invent_ref)
            p.prt(f"{referencia} soma_grades grade_invent_ref")

            if grade_pedido_ref['total'] != 0:
                grade_pedido_ref = soma_grades(gzerada, grade_pedido_ref)
                p.prt(f"{referencia} soma_grades grade_pedido_ref")
            if grade_solicitado_ref['total'] != 0:
                grade_solicitado_ref = soma_grades(gzerada, grade_solicitado_ref)
                p.prt(f"{referencia} soma_grades grade_solicitado_ref")

            if grade_pedido_ref['total'] == 0 and grade_solicitado_ref['total'] == 0:
                grade_disponivel_ref = grade_invent_ref
            else:
                grade_disponivel_ref = copy.deepcopy(grade_invent_ref)
                if grade_pedido_ref['total'] != 0:
                    grade_disponivel_ref = subtrai_grades(
                        grade_disponivel_ref, grade_pedido_ref)
                if grade_solicitado_ref['total'] != 0:
                    grade_disponivel_ref = subtrai_grades(
                        grade_disponivel_ref, grade_solicitado_ref)
            p.prt(f"{referencia} grade_disponivel_ref")

            if grade_invent_ref['total'] != 0:
                grade_ref = {
                    'inventario': grade_invent_ref,
                    'pedido': grade_pedido_ref,
                    'solicitacoes': grade_solicitado_ref,
                    'disponivel': grade_disponivel_ref,
                    'ref': referencia,
                }

                if modelo_ant != modelo:
                    grade_ref.update({
                        'modelo': modelo,
                    })
                    modelo_ant = modelo

                grades.append(grade_ref)

        p.prt('for referencias')
        self.context.update({
            'grades': grades,
            'referencias': referencias,
        })

    def get(self, request, *args, **kwargs):
        self.cursor = db_cursor_so(request)
        self.page = request.GET.get('page', 1)
        self.context = {}
        self.mount_context()
        return render(request, self.template_name, self.context)
