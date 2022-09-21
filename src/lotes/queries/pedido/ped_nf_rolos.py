from pprint import pprint

from utils.functions.queries import debug_cursor_execute
from utils.functions.models.dictlist import dictlist_lower


def query(cursor, op):
    sql = f"""
        SELECT
          rc.ORDEM_PRODUCAO op
        , ro.NOTA_FISCAL_ENT nf
        , ro.PANOACAB_NIVEL99 nivel
        , ro.PANOACAB_GRUPO ref
        , ro.PANOACAB_SUBGRUPO tam
        , ro.PANOACAB_ITEM cor
        , sum(rc.QTDE_KG_FINAL) qtd
        FROM PCPT_020 ro -- cadastro de rolos
        LEFT JOIN PCPT_025 rc -- alocação de rolo para OP
          ON rc.CODIGO_ROLO = ro.CODIGO_ROLO
        WHERE rc.ORDEM_PRODUCAO =  {op}
        GROUP BY 
          rc.ORDEM_PRODUCAO
        , ro.NOTA_FISCAL_ENT
        , ro.PANOACAB_NIVEL99
        , ro.PANOACAB_GRUPO
        , ro.PANOACAB_SUBGRUPO
        , ro.PANOACAB_ITEM
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
