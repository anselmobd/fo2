from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.functions import untuple_keys_concat

from cd.queries.novo_modulo.solicitacoes import get_solicitacao


class Solicitacao(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Solicitacao, self).__init__(*args, **kwargs)
        self.template_name = 'cd/novo_modulo/solicitacao.html'
        self.title_name = 'Solicitação'
        self.get_args = ['solicitacao']
        self.get_args2context = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = get_solicitacao(cursor, self.context['solicitacao'])

        for row in data:
            if not row['codigo_estagio']:
                row['codigo_estagio'] = 'Finalizado'
            row['int_parc'] = 'Inteiro' if row['qtde'] == row['qtd_ori'] else 'parcial'

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
            'data': data,
        })
