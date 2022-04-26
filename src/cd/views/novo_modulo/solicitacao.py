import copy
from operator import itemgetter
from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.functions import untuple_keys_concat
from utils.functions.dictlist.dictlist_to_grade import filter_dictlist_to_grade_qtd
from utils.functions.dictlist.operacoes_grade import OperacoesGrade
from utils.functions.models import dict_list_to_dict
from utils.functions.strings import only_digits
from utils.views import totalize_data

from lotes.queries.pedido import ped_inform
from cd.queries.novo_modulo.solicitacoes import get_solicitacao


class Solicitacao(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Solicitacao, self).__init__(*args, **kwargs)
        self.template_name = 'cd/novo_modulo/solicitacao.html'
        self.title_name = 'Solicitação'
        self.get_args = ['solicitacao']
        self.get_args2context = True

    def monta_dados_solicitados(self):
        self.dados_solicitados = get_solicitacao(self.cursor, self.context['solicitacao'])

    def context_solicitados(self):
        for row in self.dados_solicitados:
            row['ordem_producao|LINK'] = reverse(
                'producao:op__get',
                args=[row['ordem_producao']],
            )
            row['ordem_producao|GLYPHICON'] = '_'
            row['ordem_producao|TARGET'] = '_blank'

            row['lote|LINK'] = reverse(
                'producao:posicao__get',
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

        totalize_data(self.dados_solicitados, {
            'sum': [
                'qtde',
            ],
            'count': [],
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
                'Referência',
                'Tamanho',
                'Cor',
                'Pedido destino',
                'Referência',
                'Tamanho',
                'Cor',
                'Qtde.',
                'Parcial?',
                'Alter.',
                'OP destino',
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
            ],
            'style': untuple_keys_concat({
                (1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16):
                    'text-align: center;',
                (5, 13): 'text-align: right;',
            }),
            'data': self.dados_solicitados,
        })

    def monta_dados_pedidos(self):
        dict_pedidos = {}
        for row in self.dados_solicitados:
            pedido = row['pedido_destino']
            if pedido not in dict_pedidos:
                dict_pedidos[pedido] = {'qtde': 0}
            dict_pedidos[pedido]['qtde'] += row['qtde']

        pedidos_tuple = tuple(dict_pedidos.keys())

        pedidos_info = dict_list_to_dict(
            ped_inform(self.cursor, pedidos_tuple),
            'PEDIDO_VENDA',
        )

        self.dados_pedidos = [
            {
                'pedido': pedido,
                'cliente': (
                    pedidos_info[pedido]['CLIENTE']
                    if pedido in pedidos_info
                    else '-'
                ),
                'qtde': dict_pedidos[pedido]['qtde'],
            }
            for pedido in dict_pedidos
        ]

    def context_pedidos(self):
        totalize_data(self.dados_pedidos, {
            'sum': [
                'qtde',
            ],
            'count': [],
            'descr': {'pedido': 'Total:'},
            'row_style': 'font-weight: bold;',
            'flags': ['NO_TOT_1'],
        })

        self.context.update({
            'p_headers': ["Pedido", "Cliente", "Quantidade"],
            'p_fields': ['pedido', 'cliente', 'qtde'],
            'p_style': {
                3: 'text-align: right;'
            },
            'p_data': self.dados_pedidos,
        })

    def monta_grades_solicitadas(self):
        refs_solicitadas_set = set()
        for row in self.dados_solicitados:
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

        self.grades_solicitadas = []
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
                    self.grades_solicitadas.append(total_modelo)
                total_modelo = None

            grade_ref = filter_dictlist_to_grade_qtd(
                self.dados_solicitados,
                field_filter='ref',
                facade_filter='referencia',
                value_filter=ref['ref'],
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


            self.grades_solicitadas.append(grade_ref)

        if quant_refs_modelo > 1:
            total_modelo.update({
                'modelo': modelo_ant,
                'ref': 'total',
            })
            self.grades_solicitadas.append(total_modelo)

    def context_grades_solicitadas(self):
        self.context.update({
            'grades_solicitadas': self.grades_solicitadas,
        })

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        self.og = OperacoesGrade()

        self.monta_dados_solicitados()

        self.monta_dados_pedidos()

        self.monta_grades_solicitadas()

        self.context_solicitados()

        self.context_pedidos()

        self.context_grades_solicitadas()
