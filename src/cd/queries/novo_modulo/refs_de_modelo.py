from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import modelo_de_ref


def to_set(cursor, modelo, com_op=None, com_ped=None):
    data = query(cursor, modelo, com_op)
    return set([
        row['ref']
        for row in data
    ])

def query(cursor, modelo, com_op=True, com_ped=False):
    filtra_com_op = f"""--
        AND EXISTS (
          SELECT 
            1
          FROM pcpc_020 op 
          WHERE op.REFERENCIA_PECA = r.REFERENCIA 
            AND op.COD_CANCELAMENTO = 0
        )
    """ if com_op else ''
    filtra_com_ped = f"""--
        AND EXISTS (
          SELECT 
            1
          FROM PEDI_110 iped -- item de pedido de venda
          JOIN PEDI_100 cped -- capa de pedido de venda
            ON iped.PEDIDO_VENDA = cped.PEDIDO_VENDA
          WHERE iped.CD_IT_PE_GRUPO = r.REFERENCIA 
            AND iped.CD_IT_PE_NIVEL99 = 1
            AND cped.CODIGO_EMPRESA = 1
            AND cped.COD_CANCELAMENTO = 0
        )
    """ if com_ped else ''
    sql = f"""
        SELECT 
          r.REFERENCIA REF
        FROM BASI_030 r
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.DESCR_REFERENCIA NOT LIKE '-%'
          {filtra_com_op} -- filtra_com_op
          {filtra_com_ped} -- filtra_com_ped
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)
    return [
        row
        for row in dados        
        if modelo_de_ref(row['ref']) == modelo
    ]
