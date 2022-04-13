from pprint import pprint

from utils.functions.queries import debug_cursor_execute


def tira_lote(cursor, lote):
    sql = f"""
        DELETE FROM SYSTEXTIL.ENDR_014
        WHERE ORDEM_CONFECCAO = '{lote}'
    """
    try:
        debug_cursor_execute(cursor, sql)
    except Exception as e:
        return repr(e)
