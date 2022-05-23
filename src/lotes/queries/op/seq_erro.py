from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


def lista_op(cursor):
    sql = f"""
        WITH op_erro AS 
        ( SELECT DISTINCT  
            l.ORDEM_PRODUCAO OP
          FROM PCPC_040 l
          WHERE l.SEQUENCIA_ESTAGIO = 0
          ORDER BY 
            l.ORDEM_PRODUCAO
        )
        SELECT
          oe.OP
        , op.REFERENCIA_PECA REF
        , op.ALTERNATIVA_PECA ALT
        , op.ROTEIRO_PECA ROT
        FROM op_erro oe
        JOIN PCPC_020 op
          ON op.ORDEM_PRODUCAO = oe.OP
        WHERE op.COD_CANCELAMENTO = 0 
        ORDER BY
          oe.OP
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)