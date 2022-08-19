from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, nivel, ref):
    sql = f"""
        SELECT
          p.SUBGRU_ESTRUTURA TAM
        , p.ITEM_ESTRUTURA COR
        , p.CODIGO_DEPOSITO || ' - ' || d.DESCRICAO DEPOSITO
        , p.ESTOQUE_MINIMO
        , p.ESTOQUE_MAXIMO
        , p.TEMPO_REPOSICAO LEAD
        FROM BASI_015 p
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = p.SUBGRU_ESTRUTURA
        JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = p.CODIGO_DEPOSITO
        WHERE p.NIVEL_ESTRUTURA = {nivel}
          AND p.GRUPO_ESTRUTURA = '{ref}'
        ORDER BY
          t.ORDEM_TAMANHO
        , p.ITEM_ESTRUTURA
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
