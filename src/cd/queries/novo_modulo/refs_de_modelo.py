from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import modelo_de_ref


def to_set(cursor, modelo):
    data = query(cursor, modelo)
    return set([
        row['ref']
        for row in data
    ])

def query(cursor, modelo, com_op=True):
    filtra_com_op = f"""--
        AND EXISTS (
          SELECT 
            1
          FROM pcpc_020 op 
          WHERE op.REFERENCIA_PECA = r.REFERENCIA 
            AND op.COD_CANCELAMENTO = 0
        )
    """ if com_op else ''
    sql = f"""
        SELECT 
          r.REFERENCIA REF
        FROM BASI_030 r
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.DESCR_REFERENCIA NOT LIKE '-%'
          {filtra_com_op} -- filtra_com_op
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)
    return [
        row
        for row in dados        
        if modelo_de_ref(row['ref']) == modelo
    ]
