from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, op):
    """Busca itens de OP
    Parametro:
        op - uma OP ou uma lista de OPs
    Retorno:
        dictlist
    """
    
    if not op:
        return []

    if isinstance(op, (tuple, list)):
        ops = ", ".join(map(str, op))
        condicao = f"IN ({ops})"
    else:
        condicao = f"= {op}"
    filtra_op = f"""--
        AND l.ORDEM_PRODUCAO {condicao}
    """

    sql = f"""
        SELECT
          l.PROCONF_NIVEL99 NIVEL
        , l.PROCONF_GRUPO REF
        , l.PROCONF_ITEM COR
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO TAM
        , sum(l.QTDE_PECAS_PROG) MOV_QTD
        , l.ORDEM_PRODUCAO OP
        FROM PCPC_040 l -- lotes
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
          AND l.SEQUENCIA_ESTAGIO = 1
          {filtra_op} -- filtra_op
        GROUP BY 
          l.PROCONF_NIVEL99
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        , l.ORDEM_PRODUCAO
        ORDER BY 
          l.PROCONF_NIVEL99
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        , l.ORDEM_PRODUCAO
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        row['item'] = '.'.join([
            row['nivel'],
            row['ref'],
            row['tam'],
            row['cor'],
        ])

    return dados
