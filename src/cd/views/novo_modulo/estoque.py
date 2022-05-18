from pprint import pprint

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView
from utils.classes import Perf
from utils.functions.functions import untuple_keys_concat

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
        self.referencia = None if self.referencia == '' else self.referencia
        self.modelo = None if self.modelo == '' else int(self.modelo)

        lotes_em_estoque = LotesEmEstoque(
            self.cursor,
            tipo='iq',
            lote=self.lote,
            ref=self.referencia,
            modelo=self.modelo,
            fields_tuple=(
                'tam',
                'cor',
                'op',
                'lote',
                'qtd_prog',
                'qtd_dbaixa',
                'palete',
            ),
        )

        lotes = lotes_em_estoque.dados()
        
        lotes = paginator_basic(lotes, lotes_por_pagina, self.page)
        # pprint(lotes.__dict__)

        self.context.update({
            'headers': [
                'Palete',
                'Modelo',
                'Ref.',
                'Tam.',
                'Cor',
                'OP',
                'Lote',
                'Qtd.Original',
                'Qtd.',
            ],
            'fields': [
                'palete',
                'modelo',
                'ref',
                'tam',
                'cor',
                'op',
                'lote',
                'qtd_prog',
                'qtd_dbaixa',
            ],
            'style': untuple_keys_concat({
                (5, ): 'text-align: center;',
                (8, 9): 'text-align: right;',
            }),
            'data': lotes,
        })
