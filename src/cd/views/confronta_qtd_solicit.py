from collections import namedtuple
from pprint import pprint

from numpy import append

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.functions import untuple_keys_concat
from utils.functions.logica import compare
from utils.table_defs import TableDefs

from lotes.models.inventario import (
    Inventario,
    InventarioLote,
)

from cd.forms import ConfrontaQtdLoteForm
from cd.queries.inventario_lote import get_qtd_lotes_63
from cd.queries.mount.records import Records


class ConfrontaQtdSolicit(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(ConfrontaQtdSolicit, self).__init__(*args, **kwargs)
        self.template_name = 'cd/confronta_qtd_solicit.html'
        self.title_name = 'Confronta quant. solicitadas'

        self.SolicOpOc = namedtuple('SolicOpOc', 'op oc')

    def mount_data(self):
        self.cursor = db_cursor_so(self.request)

        records = Records(
            self.cursor,
            table='sl',
            filter={
                'sl.sit': 4,
            },
            select=(
                'sl.sol',
                'sl.op',
                'sl.oc',
                'l_63.qtd qtd_lote',
                'l_63.ref',
                'sl.qtd qtd_sol',
            )
        ).data()

        lotes = {}
        for rec in records:
            op_oc = self.SolicOpOc(
                rec['op'],
                rec['oc'],
            )
            if op_oc not in lotes:
                lotes[op_oc] = {
                    'qtd_lote': rec['qtd_lote'],
                    'qtd_sols': 0,
                    'sols': set(),
                }
            lotes[op_oc]['qtd_sols'] += rec['qtd_sol']
            lotes[op_oc]['sols'].add(f"{rec['sol']}")

        data = []
        for op_oc in lotes:
            qtd_lote = lotes[op_oc]['qtd_lote']
            qtd_sols = lotes[op_oc]['qtd_sols']
            if qtd_lote < qtd_sols:
                sols = sorted(list(lotes[op_oc]['sols']))
                data.append({
                    'op': op_oc.op,
                    'oc': op_oc.oc,
                    'qtd_lote': qtd_lote,
                    'qtd_sols': qtd_sols,
                    'sols': ', '.join(sols),
                })

        pprint(data)
        return data

    def mount_context(self):
        data = self.mount_data()

        self.table_defs = TableDefs(
            {
                'op': ['OP'],
                'oc': ['OC'],
                'qtd_lote': ['Qtd. lote', 'r'],
                'qtd_sols': ['Qtd. solicit.', 'r'],
                'sols': ['Solicitações'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

        self.context.update(self.table_defs.hfs_dict())
        self.context.update({
            'data': data,
        })
