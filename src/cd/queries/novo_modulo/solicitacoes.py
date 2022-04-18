from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


def get_solicitacoes(cursor):
    sql = f"""
        SELECT DISTINCT
          sl.SOLICITACAO 
        FROM pcpc_044 sl -- solicitação / lote 
        WHERE sl.SOLICITACAO IS NOT NULL 
        ORDER BY 
          sl.SOLICITACAO 
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
