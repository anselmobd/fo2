from django.db import connections

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all_ = ['get_dados_nf']


def get_dados_nf(cursor, nf):
    sql = f"""
        SELECT
          f.NUM_NOTA_FISCAL nf_num
        , f.SERIE_NOTA_FISC nf_ser
        , f.QTDE_EMBALAGENS vols
        , f.PESO_BRUTO peso_tot
        , f.PEDIDO_VENDA ped
        FROM FATU_050 f
        WHERE f.CODIGO_EMPRESA = 1
          AND f.NUM_NOTA_FISCAL = {nf}
          AND f.NUMERO_CAIXA_ECF = 0
    """
    debug_cursor_execute(cursor, sql, [])
    return dictlist_lower(cursor)
