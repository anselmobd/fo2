from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower
from utils.functions.queries import debug_cursor_execute


def roteiro_sem_sequencia(cursor):
    sql = """
        SELECT
          r.GRUPO_ESTRUTURA REF
        , r.SUBGRU_ESTRUTURA TAM
        , r.ITEM_ESTRUTURA COR
        , r.NUMERO_ALTERNATI ALT
        , r.NUMERO_ROTEIRO ROT
        FROM MQOP_050 r 
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.SEQUENCIA_ESTAGIO = 0
        GROUP BY 
          r.GRUPO_ESTRUTURA
        , r.SUBGRU_ESTRUTURA 
        , r.ITEM_ESTRUTURA
        , r.NUMERO_ALTERNATI
        , r.NUMERO_ROTEIRO
        ORDER BY 
          r.GRUPO_ESTRUTURA
        , r.SUBGRU_ESTRUTURA 
        , r.ITEM_ESTRUTURA
        , r.NUMERO_ALTERNATI
        , r.NUMERO_ROTEIRO
    """
    debug_cursor_execute(cursor, sql)
    return rows_to_dict_list_lower(cursor)
