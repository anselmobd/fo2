from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.queries.corte import nf_envio_msg

__all__ = ['verifica_novos']


def verifica_novos(cursor):
    data = nf_envio_msg.query(cursor)
    pprint(data)
