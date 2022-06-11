import copy
from operator import itemgetter
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.paginator import list_paginator_basic
from base.views import O2BaseGetPostView
from utils.classes import Perf
from utils.functions.dictlist.dictlist_to_grade import filter_dictlist_to_grade_qtd

from comercial.queries import modelos_tabela_preco


from utils.functions.dictlist import (
    operacoes_grade,
    operacoes_dictlist,
)

from cd.forms.disponibilidade import DisponibilidadeForm
from cd.queries.novo_modulo.lotes_em_estoque import LotesEmEstoque
from cd.queries.novo_modulo import refs_em_palets


class Disponibilidade(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self):
        super(Disponibilidade, self).__init__()
        self.permission_required = 'cd.can_view_grades_estoque'
        self.Form_class = DisponibilidadeForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/disponibilidade.html'
        self.title_name = 'Disponibilidade'

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
        self.modelo = None if self.modelo == '' else int(self.modelo)

        referencias = refs_em_palets.query(
            self.cursor,
            ref=self.referencia,
            colecao=colecao_codigo,
            modelo=self.modelo,
        )
        p.prt('referencias')

        if tabela_codigo:
            modelos_tabela = modelos_tabela_preco(self.cursor, tabela_codigo)
            filtra_modelo = lambda row: row['modelo'] in modelos_tabela
        else:
            filtra_modelo = lambda row: True

        modelos = sorted(list(set([
            row['modelo']
            for row in referencias
            if filtra_modelo(row)
        ])))

        qtd_referencias = sum([
            row['modelo'] in modelos
            for row in referencias
        ])

        self.context.update({
            'qtd_modelos': len(modelos),
            'qtd_referencias': qtd_referencias,
        })

        if qtd_referencias == 0:
            self.context.update({
                'erro': "Nenhuma referência selecionada",
            })
            return            

        dados_modelos, modelos = list_paginator_basic(
            modelos, modelos_por_pagina, self.page)

        referencias = sorted(
            [
                row
                for row in referencias
                if row['modelo'] in modelos
            ],
            key=itemgetter('modelo', 'ref')
        )
        p.prt('paginator')

        filtra_ref = [
            row['ref']
            for row in referencias
        ]

        inventario = refs_em_palets.query(
            self.cursor,
            fields='inv',
            ref=filtra_ref,
            com_qtd_63=True,
        )
        p.prt('inventario')

        empenhado = refs_em_palets.query(
            self.cursor,
            fields='emp',
            ref=filtra_ref,
            com_qtd_63=True,
        )
        p.prt('empenhado')

        solicitado = refs_em_palets.query(
            self.cursor,
            fields='sol',
            ref=filtra_ref,
            com_qtd_63=True,
        )
        p.prt('solicitado')

        # ped_solit = odl.merge(empenhado, solicitado, ['op', 'oc'], ['qtd'])
        # p.prt('ped_solit')

        grades = []
        modelo_ant = -1
        quant_refs_modelo = 1
        total_modelo = None
        quant_refs_geral = 0
        total_geral = None
        for row_ref in referencias:
            quant_refs_geral += 1
            referencia = row_ref['ref']
            modelo = row_ref['modelo']

            if modelo_ant not in (-1, modelo):
                if self.apresenta == 't' or quant_refs_modelo > 1:
                    grades.append({
                        'disponivel': total_modelo,
                        'total_modelo': modelo_ant,
                    })
                total_modelo = None

            gzerada = None
    
            grade_invent_ref = self.grade_dados(inventario, referencia)
            gzerada = og.update_gzerada(gzerada, grade_invent_ref)
            p.prt(f"{referencia} grade_invent_ref")

            grade_empenhado_ref = self.grade_dados(empenhado, referencia)
            if grade_empenhado_ref['total'] != 0:
                gzerada = og.update_gzerada(gzerada, grade_empenhado_ref)
            p.prt(f"{referencia} grade_pedido_ref")

            grade_solicitado_ref = self.grade_dados(solicitado, referencia)
            if grade_solicitado_ref['total'] != 0:
                gzerada = og.update_gzerada(gzerada, grade_solicitado_ref)
            p.prt(f"{referencia} grade_solicitado_ref")

            # grade_ped_solit_ref = self.grade_dados(ped_solit, referencia)
            # p.prt(f"{referencia} grade_ped_solit_ref")

            grade_invent_ref = og.soma_grades(gzerada, grade_invent_ref)
            p.prt(f"{referencia} soma_grades grade_invent_ref")

            if grade_empenhado_ref['total'] != 0:
                grade_empenhado_ref = og.soma_grades(gzerada, grade_empenhado_ref)
                p.prt(f"{referencia} soma_grades grade_pedido_ref")

            if grade_solicitado_ref['total'] != 0:
                grade_solicitado_ref = og.soma_grades(gzerada, grade_solicitado_ref)
                p.prt(f"{referencia} soma_grades grade_solicitado_ref")

            # grade_ped_solit_ref = og.soma_grades(gzerada, grade_ped_solit_ref)
            # p.prt(f"{referencia} soma_grades grade_ped_solit_ref")

            if grade_empenhado_ref['total'] == 0 and grade_solicitado_ref['total'] == 0:
                grade_disponivel_ref = grade_invent_ref
            else:
                grade_disponivel_ref = copy.deepcopy(grade_invent_ref)
                if grade_empenhado_ref['total'] != 0:
                    grade_disponivel_ref = og.subtrai_grades(
                        grade_disponivel_ref, grade_empenhado_ref)
                if grade_solicitado_ref['total'] != 0:
                    grade_disponivel_ref = og.subtrai_grades(
                        grade_disponivel_ref, grade_solicitado_ref)
                # grade_disponivel_ref = og.subtrai_grades(
                #     grade_disponivel_ref, grade_ped_solit_ref)
            p.prt(f"{referencia} grade_disponivel_ref")

            if total_modelo:
                total_modelo = og.soma_grades(total_modelo, grade_disponivel_ref)
            else:
                total_modelo = copy.deepcopy(grade_disponivel_ref)

            if total_geral:
                total_geral = og.soma_grades(total_geral, grade_disponivel_ref)
            else:
                total_geral = copy.deepcopy(grade_disponivel_ref)

            grade_ref = {
                'disponivel': grade_disponivel_ref,
                'ref': referencia,
            }

            if self.apresenta == 'g':
                grade_ref.update({
                    'inventario': grade_invent_ref,
                    'pedido': grade_empenhado_ref,
                    'solicitacoes': grade_solicitado_ref,
                })

            if modelo_ant == modelo:
                quant_refs_modelo += 1
            else:
                quant_refs_modelo = 1
                grade_ref.update({
                    'modelo': modelo,
                })
                modelo_ant = modelo

            if self.apresenta != 't':
                grades.append(grade_ref)

        if self.apresenta == 't' or quant_refs_modelo > 1:
            grades.append({
                'disponivel': og.grade_filtra_linhas_zeradas(total_modelo, total_field='total'),
                'total_modelo': modelo_ant,
            })

        if quant_refs_geral > 1:
            grades.append({
                'disponivel': og.grade_filtra_linhas_zeradas(total_geral, total_field='total'),
                'total_modelo': 'geral',
            })

        p.prt('for referencias')
        self.context.update({
            'grades': grades,
            'modelos_por_pagina': modelos_por_pagina,
            'dados': dados_modelos,
        })
