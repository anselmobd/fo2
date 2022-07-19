from pprint import pprint

from django.db import DatabaseError, transaction
from utils.functions.queries import debug_cursor_execute


def reativa_op(cursor, op):

    def update_op():
        sql = f"""
            UPDATE PCPC_020 o -- op
            SET
              o.SITUACAO = 4
            , o.COD_CANCELAMENTO = 0
            , o.DT_CANCELAMENTO = NULL
            WHERE 1=1
              AND o.ORDEM_PRODUCAO = {op}
              AND o.SITUACAO <> 4
              AND o.COD_CANCELAMENTO <> 0
              -- AND o.DT_CANCELAMENTO IS NOT NULL
        """
        debug_cursor_execute(cursor, sql)

    def update_lotes():
        sql = f"""
            UPDATE PCPC_040 l -- lote
            SET
              l.SITUACAO_ORDEM = 1 
            WHERE 1=1
              AND l.ORDEM_PRODUCAO = {op}
              AND l.SITUACAO_ORDEM <> 1
        """
        debug_cursor_execute(cursor, sql)

    try:
        with transaction.atomic():
            update_op()
            update_lotes()
    except DatabaseError:
        return False
    return True
