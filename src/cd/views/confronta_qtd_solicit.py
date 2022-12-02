from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from o2.views.base.get import O2BaseGetView
from utils.table_defs import TableDefs

from cd.queries import inconsist_qtd_solicit

class ConfrontaQtdSolicit(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(ConfrontaQtdSolicit, self).__init__(*args, **kwargs)
        self.template_name = 'cd/confronta_qtd_solicit.html'
        self.title_name = 'Confronta quant. empenhadas'
        self.por_pagina = 50

        self.table_defs = TableDefs(
            {
                'op': ['OP'],
                'per': ['Período'],
                'oc': ['OC'],
                'qtd_lote': ['Qtd. lote', 'r'],
                'qtd_sols': ['Qtd. solicit.', 'r'],
                'lote': ['Lote'],
                'sols': ['Solicitações'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        page = self.request.GET.get('page', 1)

        data = inconsist_qtd_solicit.query(self.cursor)
        inconsist_len = len(data)

        data = paginator_basic(data, self.por_pagina, page)

        for row in data.object_list:
            row['lote|LINK'] = reverse(
                'producao:lote__get', args=[row['lote']])

        self.context.update(self.table_defs.hfs_dict())
        self.context.update({
            'data': data,
            'safe': ['op', 'per', 'oc', 'lote', 'sols'],
            'por_pagina': self.por_pagina,
            'inconsist_len': inconsist_len,
        })
