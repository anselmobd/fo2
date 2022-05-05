import copy
from operator import itemgetter
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.paginator import list_paginator_basic
from base.views import O2BaseGetPostView
from utils.classes import Perf
from utils.functions.dictlist.dictlist_to_grade import filter_dictlist_to_grade_qtd
from utils.functions.strings import only_digits

from comercial.queries import itens_tabela_preco


from utils.functions.dictlist import (
    operacoes_grade,
    operacoes_dictlist,
)

import cd.forms
from cd.queries.novo_modulo.lotes import lotes_em_estoque


class GradeEstoqueTotais(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self):
        super(GradeEstoqueTotais, self).__init__()
        self.permission_required = 'cd.can_view_grades_estoque'
        self.Form_class = cd.forms.GradeEstoqueTotaisForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/grade_estoque_totais.html'
        self.title_name = 'Todas as grades do estoque'

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

        self.cursor = db_cursor_so(self.request)
        og = operacoes_grade.OperacoesGrade()
        odl = operacoes_dictlist.OperacoesDictList()

        modelos_por_pagina = 20
        if self.usa_paginador == 'n':
            modelos_por_pagina = 99999

        colecao_codigo = None if self.colecao == '' else self.colecao
        
        tabela_codigo = None if self.tabela == '' else self.tabela

        self.referencia = None if self.referencia == '' else self.referencia

        referencias = lotes_em_estoque(
            self.cursor, ref=self.referencia, colecao=colecao_codigo, get='ref')
        p.prt('referencias')

        if tabela_codigo:
            tabela_chunks = tabela_codigo.split('.')
            itens_tabela = itens_tabela_preco(self.cursor, *tabela_chunks)
            modelos_tabela = set([
                int(only_digits(row['grupo_estrutura']))
                for row in itens_tabela
            ])
            modelos = sorted(list(set([
                row['modelo']
                for row in referencias
                if row['modelo'] in modelos_tabela
            ])))
        else:
            modelos = sorted(list(set([
                row['modelo']
                for row in referencias
            ])))

        qtd_referencias = len([
            row
            for row in referencias
            if row['modelo'] in modelos
        ])
        self.context.update({
            'qtd_modelos': len(modelos),
            'qtd_referencias': qtd_referencias,
        })

        dados_modelos, modelos = list_paginator_basic(
            modelos, modelos_por_pagina, self.page)

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
        ped_solit = odl.merge(pedido, solicitado, ['op', 'oc'], ['qtd'])
        p.prt('ped_solit')

        grades = []
        modelo_ant = -1
        for row_ref in referencias:
            referencia = row_ref['ref']
            modelo = row_ref['modelo']

            gzerada = None
    
            grade_invent_ref = self.grade_dados(inventario, referencia)
            gzerada = og.update_gzerada(gzerada, grade_invent_ref)
            p.prt(f"{referencia} grade_invent_ref")

            grade_pedido_ref = self.grade_dados(pedido, referencia)
            if grade_pedido_ref['total'] != 0:
                gzerada = og.update_gzerada(gzerada, grade_pedido_ref)
            p.prt(f"{referencia} grade_pedido_ref")

            grade_solicitado_ref = self.grade_dados(solicitado, referencia)
            if grade_solicitado_ref['total'] != 0:
                gzerada = og.update_gzerada(gzerada, grade_solicitado_ref)
            p.prt(f"{referencia} grade_solicitado_ref")

            grade_ped_solit_ref = self.grade_dados(ped_solit, referencia)
            p.prt(f"{referencia} grade_ped_solit_ref")

            grade_invent_ref = og.soma_grades(gzerada, grade_invent_ref)
            p.prt(f"{referencia} soma_grades grade_invent_ref")

            if grade_pedido_ref['total'] != 0:
                grade_pedido_ref = og.soma_grades(gzerada, grade_pedido_ref)
                p.prt(f"{referencia} soma_grades grade_pedido_ref")

            if grade_solicitado_ref['total'] != 0:
                grade_solicitado_ref = og.soma_grades(gzerada, grade_solicitado_ref)
                p.prt(f"{referencia} soma_grades grade_solicitado_ref")

            grade_ped_solit_ref = og.soma_grades(gzerada, grade_ped_solit_ref)
            p.prt(f"{referencia} soma_grades grade_ped_solit_ref")

            if grade_pedido_ref['total'] == 0 and grade_solicitado_ref['total'] == 0:
                grade_disponivel_ref = grade_invent_ref
            else:
                grade_disponivel_ref = copy.deepcopy(grade_invent_ref)
                # if grade_pedido_ref['total'] != 0:
                #     grade_disponivel_ref = og.subtrai_grades(
                #         grade_disponivel_ref, grade_pedido_ref)
                # if grade_solicitado_ref['total'] != 0:
                #     grade_disponivel_ref = og.subtrai_grades(
                #         grade_disponivel_ref, grade_solicitado_ref)
                grade_disponivel_ref = og.subtrai_grades(
                    grade_disponivel_ref, grade_ped_solit_ref)
            p.prt(f"{referencia} grade_disponivel_ref")

            grade_ref = {
                'disponivel': grade_disponivel_ref,
                'ref': referencia,
            }
            if self.apresenta == 't':
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
            'modelos_por_pagina': modelos_por_pagina,
            'dados': dados_modelos,
        })
