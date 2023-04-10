import copy
from operator import itemgetter
from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from o2.views.base.get import O2BaseGetView
from utils.functions import untuple_keys_concat
from utils.functions.dictlist.dictlist_to_grade import filter_dictlist_to_grade_qtd
from utils.functions.dictlist.operacoes_grade import OperacoesGrade
from utils.functions.models.dictlist import dictlist_indexed
from utils.functions.strings import only_digits
from utils.views import totalize_data

from lotes.queries.pedido import ped_inform
from cd.queries.novo_modulo.solicitacao import get_solicitacao


class Solicitacao(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Solicitacao, self).__init__(*args, **kwargs)
        self.template_name = 'cd/novo_modulo/solicitacao.html'
        self.title_name = 'Solicitação'
        self.get_args = ['solicitacao']
        self.get_args2context = True

    def monta_dados_solicitados(self):
        if (
            self.context['pedido']
            or self.context['ref_destino']
            or self.context['ref_reservada']
            or self.context['op']
            or self.context['lote']
        ):
            if self.sem_numero:
                solicitacao = None
            else:
                solicitacao = self.context['solicitacao']
            self.dados_solicitados = get_solicitacao(
                self.cursor,
                solicitacao=solicitacao,
                pedido_destino=self.context['pedido'],
                ref_destino=self.context['ref_destino'],
                ref_reservada=self.context['ref_reservada'],
                op=self.context['op'],
                lote=self.context['lote'],
            )
        else:
            if self.sem_numero:
                self.dados_solicitados = []
            else:
                self.dados_solicitados = get_solicitacao(
                    self.cursor, self.context['solicitacao'])

        self.dados_enderecados = copy.deepcopy(self.dados_solicitados)
        self.dados_enderecados.sort(
            key=itemgetter(
                'rota',
                'endereco',
                'situacao',
                'ordem_producao',
                'lote',
            ),
            reverse=True,
        )

    def context_solicitados(self):

        self.dados_solicitados = paginator_basic(
            self.dados_solicitados, self.por_pagina, self.page_sol)

        for row in self.dados_solicitados.object_list:
            row['ordem_producao|LINK'] = reverse(
                'producao:op__get',
                args=[row['ordem_producao']],
            )
            row['ordem_producao|GLYPHICON'] = '_'
            row['ordem_producao|TARGET'] = '_blank'

            row['lote|LINK'] = reverse(
                'producao:lote__get',
                args=[row['lote']],
            )
            row['lote|GLYPHICON'] = '_'
            row['lote|TARGET'] = '_blank'

            row['ref|LINK'] = reverse(
                'produto:ref__get',
                args=[row['ref']],
            )
            row['ref|GLYPHICON'] = '_'
            row['ref|TARGET'] = '_blank'

            row['pedido_destino|LINK'] = reverse(
                'producao:pedido__get',
                args=[row['pedido_destino']],
            )
            row['pedido_destino|GLYPHICON'] = '_'
            row['pedido_destino|TARGET'] = '_blank'

            row['grupo_destino|LINK'] = reverse(
                'produto:ref__get',
                args=[row['grupo_destino']],
            )
            row['grupo_destino|GLYPHICON'] = '_'
            row['grupo_destino|TARGET'] = '_blank'

            row['inclusao'] = row['inclusao'].strftime("%d/%m/%y %H:%M")

        totalize_data(self.dados_solicitados.object_list, {
            'sum': ['qtde'],
            'descr': {'situacao': 'Total:'},
            'row_style': 'font-weight: bold;',
            'flags': ['NO_TOT_1'],
        })

        self.context.update({
            'headers': [
                'Situação',
                'Estágio',
                'OP',
                'Lote',
                'Qtd.Lote',
                'Ref.',
                'Tam.',
                'Cor',
                'Pedido destino',
                'Ref.',
                'Tam.',
                'Cor',
                'Qtde.',
                'Parcial?',
                'Alter.',
                'OP destino',
                'Inclusão S.',
            ],
            'fields': [
                'situacao',
                'codigo_estagio',
                'ordem_producao',
                'lote',
                'qtd_ori',
                'ref',
                'tam',
                'cor',
                'pedido_destino',
                'grupo_destino',
                'sub_destino',
                'cor_destino',
                'qtde',
                'int_parc',
                'alter_destino',
                'op_destino',
                'inclusao',
            ],
            'style': untuple_keys_concat({
                (1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16):
                    'text-align: center;',
                (5, 13): 'text-align: right;',
            }),
            'data': self.dados_solicitados,
        })

    def context_enderecos(self):
        self.dados_enderecados = paginator_basic(
            self.dados_enderecados, self.por_pagina, self.page_end)

        for row in self.dados_enderecados.object_list:
            row['ordem_producao|LINK'] = reverse(
                'producao:op__get',
                args=[row['ordem_producao']],
            )
            row['ordem_producao|GLYPHICON'] = '_'
            row['ordem_producao|TARGET'] = '_blank'

            row['lote|LINK'] = reverse(
                'producao:lote__get',
                args=[row['lote']],
            )
            row['lote|GLYPHICON'] = '_'
            row['lote|TARGET'] = '_blank'

            row['ref|LINK'] = reverse(
                'produto:ref__get',
                args=[row['ref']],
            )
            row['ref|GLYPHICON'] = '_'
            row['ref|TARGET'] = '_blank'

            row['inclusao'] = row['inclusao'].strftime("%d/%m/%y %H:%M")

            if row['inclusao_palete']:
                row['inclusao_palete'] = row['inclusao_palete'].strftime("%d/%m/%y %H:%M")
            else:
                row['inclusao_palete'] = '-'

            if row['inclusao_endereco']:
                row['inclusao_endereco'] = row['inclusao_endereco'].strftime("%d/%m/%y %H:%M")
            else:
                row['inclusao_endereco'] = '-'

        totalize_data(self.dados_enderecados.object_list, {
            'sum': ['qtde'],
            'descr': {'situacao': 'Total:'},
            'row_style': 'font-weight: bold;',
            'flags': ['NO_TOT_1'],
        })

        self.context.update({
            'e_headers': [
                'Situação',
                'Estágio',
                'OP',
                'Lote',
                'Qtd.Lote',
                'Ref.',
                'Tam.',
                'Cor',
                'Qtde.',
                'Parcial?',
                'Inclusão S.',
                'Palete',
                'Inclusão P.',
                'Rota',
                'Endereço',
                'Inclusão E.',
            ],
            'e_fields': [
                'situacao',
                'codigo_estagio',
                'ordem_producao',
                'lote',
                'qtd_ori',
                'ref',
                'tam',
                'cor',
                'qtde',
                'int_parc',
                'inclusao',
                'palete',
                'inclusao_palete',
                'rota',
                'endereco',
                'inclusao_endereco',

            ],
            'e_style': untuple_keys_concat({
                (1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16):
                    'text-align: center;',
                (5, 9): 'text-align: right;',
            }),
            'e_data': self.dados_enderecados,
        })

    def monta_dados_pedidos(self):
        if not self.dados_solicitados:
            self.dados_pedidos = []
            return

        dict_pedidos = {}
        for row in self.dados_solicitados:
            pedido = row['pedido_destino']
            if pedido not in dict_pedidos:
                dict_pedidos[pedido] = {'qtde': 0}
            dict_pedidos[pedido]['qtde'] += row['qtde']

        pedidos_tuple = tuple(dict_pedidos.keys())

        pedidos_info = dictlist_indexed(
            ped_inform(self.cursor, pedidos_tuple),
            'PEDIDO_VENDA',
        )

        def dt_embarque(info, pedido):
            try:
                return info[pedido]['DT_EMBARQUE'].date()
            except Exception:
                return "-"

        self.dados_pedidos = [
            {
                'pedido': pedido,
                'cliente': (
                    pedidos_info[pedido]['CLIENTE']
                    if pedido in pedidos_info
                    else '-'
                ),
                'dt_embarque': dt_embarque(pedidos_info, pedido),
                'qtde': dict_pedidos[pedido]['qtde'],
            }
            for pedido in dict_pedidos
        ]

    def context_pedidos(self):
        totalize_data(self.dados_pedidos, {
            'sum': ['qtde'],
            'descr': {'pedido': 'Total:'},
            'row_style': 'font-weight: bold;',
            'flags': ['NO_TOT_1'],
        })

        self.context.update({
            'p_headers': ["Pedido", "Cliente", "Data embarque", "Quantidade"],
            'p_fields': ['pedido', 'cliente', 'dt_embarque', 'qtde'],
            'p_style': {
                4: 'text-align: right;'
            },
            'p_data': self.dados_pedidos,
        })

    def monta_grades(self, situacao=None):
        if not self.dados_solicitados:
            self.grades_solicitadas = []
            return

        refs_solicitadas_set = set()
        for row in self.dados_solicitados:
            if not situacao or row['situacao'] == situacao:
                refs_solicitadas_set.add(row['ref'])

        refs_solicitadas = []
        for ref in refs_solicitadas_set:
            refs_solicitadas.append({
                'ref': ref,
                'modelo': int(only_digits(ref)),
            })

        refs_solicitadas = sorted([
            row
            for row in refs_solicitadas
        ], key=itemgetter('modelo', 'ref'))

        grades_solicitadas = []
        modelo_ant = -1
        quant_refs_modelo = 1
        total_modelo = None
        for ref in refs_solicitadas:
            if modelo_ant not in (-1, ref['modelo']):
                if quant_refs_modelo > 1:
                    total_modelo.update({
                        'modelo': modelo_ant,
                        'ref': 'total',
                    })
                    grades_solicitadas.append(total_modelo)
                total_modelo = None

            if situacao:
                field_filter = ('situacao', 'ref')
                value_filter = (situacao, ref['ref'])
            else:
                field_filter = 'ref'
                value_filter = ref['ref']

            grade_ref = filter_dictlist_to_grade_qtd(
                self.dados_solicitados,
                field_filter=field_filter,
                facade_filter='referencia',
                value_filter=value_filter,
                field_linha='cor',
                field_coluna='tam',
                facade_coluna='Tamanho',
                field_quantidade='qtde',
            )
            grade_ref = self.og.ordena_tamanhos(grade_ref)

            if total_modelo:
                total_modelo = self.og.soma_grades(total_modelo, grade_ref)
            else:
                total_modelo = copy.deepcopy(grade_ref)

            grade_ref.update({
                'ref': ref['ref'],
            })
            if modelo_ant == ref['modelo']:
                quant_refs_modelo += 1
            else:
                quant_refs_modelo = 1
                grade_ref.update({
                    'modelo': ref['modelo'],
                })
                modelo_ant = ref['modelo']


            grades_solicitadas.append(grade_ref)

        if quant_refs_modelo > 1:
            total_modelo.update({
                'modelo': modelo_ant,
                'ref': 'total',
            })
            grades_solicitadas.append(total_modelo)

        return grades_solicitadas

    def monta_grades_solicitadas(self):
        self.grades_solicitadas = self.monta_grades()

    def context_grades_solicitadas(self):
        self.context.update({
            'grades_solicitadas': self.grades_solicitadas,
        })

    def monta_grades_situacao(self):
        self.grades_situacao = []
        if not self.dados_solicitados:
            self.grades_solicitadas = []
            return

        situacoes_set = set()
        for row in self.dados_solicitados:
            situacoes_set.add(row['situacao'])

        situacoes_list = list(situacoes_set)
        situacoes_list.sort()

        for situacao in situacoes_list:
            self.grades_situacao.append({
                'situacao': situacao,
                'grades': self.monta_grades(situacao),
            })


    def context_grades_situacao(self):
        self.context.update({
            'grades_situacao': self.grades_situacao,
        })

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        self.por_pagina = 100
        self.page_sol = self.request.GET.get('page_sol', 1)
        self.context['page_end'] = self.request.GET.get('page_end', 0)
        self.page_end = self.request.GET.get('page_end', 1)
        self.context['aba'] = self.request.GET.get('aba', 'default')

        self.og = OperacoesGrade()

        self.sem_numero = self.context['solicitacao'] == 'sn'
        if self.sem_numero:
            self.context['solicitacao'] = '# (sem número)'
            self.por_pagina = 999999
        else:
            self.por_pagina = 100

        self.context['sem_numero'] = self.sem_numero
        self.context['pedido'] = self.request.GET.get('pedido', None)
        self.context['ref_destino'] = self.request.GET.get('ref_destino', None)
        self.context['ref_reservada'] = self.request.GET.get('ref_reservada', None)
        self.context['op'] = self.request.GET.get('op', None)
        self.context['lote'] = self.request.GET.get('lote', None)

        self.monta_dados_solicitados()

        self.monta_dados_pedidos()

        self.monta_grades_solicitadas()

        self.monta_grades_situacao()

        self.context_solicitados()

        self.context_enderecos()

        self.context_pedidos()

        self.context_grades_solicitadas()

        self.context_grades_situacao()