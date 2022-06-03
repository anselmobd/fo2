from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.table_defs import TableDefs

from cd.queries import inconsist_qtd_solicit

class ConfrontaQtdSolicit(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(ConfrontaQtdSolicit, self).__init__(*args, **kwargs)
        self.template_name = 'cd/confronta_qtd_solicit.html'
        self.title_name = 'Confronta quant. solicitadas'

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

        data = inconsist_qtd_solicit.query(self.cursor)

        self.context.update(self.table_defs.hfs_dict())
        self.context.update({
            'data': data,
            'safe': ['op', 'per', 'oc', 'lote', 'sols']
        })
