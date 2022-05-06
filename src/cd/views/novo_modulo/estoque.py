from pprint import pprint

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView
from utils.classes import Perf
from utils.functions.functions import untuple_keys_concat

import cd.forms
from cd.queries.novo_modulo.lotes import lotes_em_estoque


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

        lotes = lotes_em_estoque(self.cursor, tipo='iq',)
        
        lotes = paginator_basic(lotes, lotes_por_pagina, self.page)
        pprint(lotes.__dict__)

        self.context.update({
            'headers': [
                'Modelo',
                'Ref.',
                'Tam.',
                'Cor',
                'OP',
                'Período',
                'OC',
                'Qtd.Original',
                'Qtd.',
            ],
            'fields': [
                'modelo',
                'ref',
                'tam',
                'cor',
                'op',
                'per',
                'oc',
                'qtd_prog',
                'qtd_dbaixa',
            ],
            'style': untuple_keys_concat({
                (5, ): 'text-align: center;',
                (8, 9): 'text-align: right;',
            }),
            'data': lotes,
        })
