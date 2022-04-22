import copy
from operator import itemgetter
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from base.paginator import list_paginator_basic
from utils.classes import Perf
from utils.functions.dictlist import filter_dictlist_to_grade_qtd

from lotes.views.a_produzir import (
    soma_grades,
    subtrai_grades,
    update_gzerada,
)

import cd.forms
from cd.queries.novo_modulo.lotes import lotes_em_estoque


class GradeEstoqueTotais(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'cd.can_view_grades_estoque'
        self.Form_class = cd.forms.GradeEstoqueTotaisForm
        self.template_name = 'cd/novo_modulo/grade_estoque_totais.html'
        self.context = {
            'titulo': 'Todas as grades do estoque',
            'modelos_por_pagina': 20,
        }

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

    def mount_context(self, caso, page):
        self.cursor = db_cursor_so(self.request)
        p = Perf(id='GradeEstoqueTotais', on=True)

        referencias = lotes_em_estoque(self.cursor, get='ref')
        p.prt('referencias')

        modelos = sorted(list(set([
            row['modelo']
            for row in referencias
        ])))
        dados_modelos, modelos = list_paginator_basic(
            modelos, self.context['modelos_por_pagina'], page)

        referencias = sorted([
            row
            for row in referencias
            if row['modelo'] in modelos
        ], key=itemgetter('modelo', 'ref'))
        p.prt('paginator')

        filtra_ref = [
            row['ref']
            for row in referencias
        ]

        inventario = lotes_em_estoque(self.cursor, tipo='i', ref=filtra_ref)
        p.prt('inventario')
        pedido = lotes_em_estoque(self.cursor, tipo='p', ref=filtra_ref)
        p.prt('pedido')
        solicitado = lotes_em_estoque(self.cursor, tipo='s', ref=filtra_ref)
        p.prt('solicitado')

        grades = []
        modelo_ant = -1
        for row_ref in referencias:
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
                    'disponivel': grade_disponivel_ref,
                    'ref': referencia,
                }
                if caso == 't':
                    grade_ref.update({
                        'inventario': grade_invent_ref,
                        'pedido': grade_pedido_ref,
                        'solicitacoes': grade_solicitado_ref,
                    })

                if modelo_ant != modelo:
                    grade_ref.update({
                        'modelo': modelo,
                    })
                    modelo_ant = modelo

                grades.append(grade_ref)

        p.prt('for referencias')
        self.context.update({
            'grades': grades,
            'dados': dados_modelos,
        })

    def get(self, request, *args, **kwargs):
        self.request = request
        form = self.Form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        form = self.Form_class(request.POST)
        if form.is_valid():
            caso = form.cleaned_data['caso']
            page = form.cleaned_data['page']
            self.mount_context(caso, page)
        self.context['form'] = form
        return render(request, self.template_name, self.context)
