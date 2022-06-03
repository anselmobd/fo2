from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.functions import untuple_keys_concat
from utils.functions.logica import compare

from lotes.models.inventario import (
    Inventario,
    InventarioLote,
)

from cd.forms import ConfrontaQtdLoteForm
from cd.queries.inventario_lote import get_qtd_lotes_63


class ConfrontaQtdSolicit(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(ConfrontaQtdSolicit, self).__init__(*args, **kwargs)
        self.template_name = 'cd/confronta_qtd_solicit.html'
        self.title_name = 'Confronta quant. solicitadas'

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
