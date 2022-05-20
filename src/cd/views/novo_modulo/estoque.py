from pprint import pprint

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView
from utils.classes import Perf
from utils.functions.functions import untuple_keys_concat
from utils.views import totalize_data

import cd.forms
from cd.queries.novo_modulo.lotes_em_estoque import LotesEmEstoque


class NovoEstoque(O2BaseGetPostView):

    def __init__(self):
        super(NovoEstoque, self).__init__()
        self.Form_class = cd.forms.NovoEstoqueForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/estoque.html'
        self.title_name = 'Estoque'

    def mount_context(self):
        p = Perf(id='GradeEstoqueTotais', on=True)

        self.cursor = db_cursor_so(self.request)

        lotes_por_pagina = 20
        # if self.usa_paginador == 'n':
        #     modelos_por_pagina = 99999

        self.lote = None if self.lote == '' else self.lote
        self.op = None if self.op == '' else self.op
        self.referencia = None if self.referencia == '' else self.referencia
        self.cor = None if self.cor == '' else self.cor
        self.tam = None if self.tam == '' else self.tam
        self.modelo = None if self.modelo == '' else int(self.modelo)
        self.endereco = None if self.endereco == '' else self.endereco

        lotes_em_estoque = LotesEmEstoque(
            self.cursor,
            tipo='iq',
            lote=self.lote,
            ref=self.referencia,
            cor=self.cor,
            tam=self.tam,
            modelo=self.modelo,
            endereco=self.endereco,
            op=self.op,
            fields_tuple=(
                'tam',
                'cor',
                'op',
                'lote',
                'qtd_prog',
                'qtd_dbaixa',
                'palete',
                'endereco',
                'rota',
                'estagio',
                'solicitacoes',
            ),
        )

        lotes = lotes_em_estoque.dados()

        if len(lotes) == 0:
            return
        
        totalize_data(
            lotes,
            {
                'sum': ['qtd_dbaixa'],
                'descr': {'lote': 'Total geral:'}
            }
        )
        totalizador_lotes = lotes[-1]
        del(lotes[-1])

        lotes = paginator_basic(lotes, lotes_por_pagina, self.page)
        lotes.object_list.append(totalizador_lotes)

        fields = {
            'palete': 'Palete',
            'endereco': 'Endereço',
            'rota': 'Rota',
            'modelo': 'Modelo',
            'ref': 'Ref.',
            'tam': 'Tam.',
            'cor': 'Cor',
            'op': 'OP',
            'lote': 'Lote',
            'qtd_prog': 'Qtd.Original',
            'qtd_dbaixa': 'Qtd.',
            'estagio': 'Estágio',
            'solicitacoes': 'Solicitações',
        }
        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'safe': [
                'op',
            ],
            'style': untuple_keys_concat({
                (12, ): 'text-align: center;',
                (10, 11): 'text-align: right;',
            }),
            'data': lotes,
        })
