from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


def query(cursor):
    sql = f"""
        SELECT
          sl.SOLICITACAO sol
        , sl.PEDIDO_DESTINO ped
        , sl.ORDEM_PRODUCAO op
        , sl.ORDEM_CONFECCAO oc
        , sl.SITUACAO sit
        , sl.QTDE qtd_sol
        FROM PCPC_044 sl
        LEFT JOIN ENDR_014 lp
          ON lp.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND MOD(lp.ORDEM_CONFECCAO, 100000) = sl.ORDEM_CONFECCAO
        LEFT JOIN ENDR_015 ec -- endereço/container 
          ON ec.COD_CONTAINER = lp.COD_CONTAINER
        WHERE 1=1
          AND sl.ORDEM_CONFECCAO <> 0 
          AND ec.COD_ENDERECO IS NULL 
        ORDER BY 
          sl.SOLICITACAO
        , sl.PEDIDO_DESTINO
        , sl.SITUACAO
        , sl.ORDEM_PRODUCAO
        , sl.ORDEM_CONFECCAO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
