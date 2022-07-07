from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs

from logistica.forms.nf import NfForm
from logistica.queries.etiqueta_nf import dados_nf


class EtiquetaNf(O2BaseGetPostView):

    def __init__(self):
        super(EtiquetaNf, self).__init__()
        self.Form_class = NfForm
        self.cleaned_data2self = True
        self.template_name = 'logistica/etiqueta_nf.html'
        self.title_name = 'Estoque'

        self.init_defs()

    def init_defs(self):
        self.col_defs = TableDefs(
            {
                'nf_num': ["NF"],
                'nf_ser': ["Série"],
                'vols': ["Volumes"],
                'peso_tot': ["Peso Total"],
                'ped': ["Pedido Tussor"],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = dados_nf(cursor, self.nf)

        self.context = self.col_defs.hfs_dict()
        self.context.update({
            'data': data,
        })
