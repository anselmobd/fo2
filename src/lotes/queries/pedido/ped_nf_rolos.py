import collections.abc
from pprint import pprint

from utils.functions.queries import debug_cursor_execute
from utils.functions.models.dictlist import dictlist_lower


def query(cursor, op):
    if (not isinstance(op, collections.abc.Sequence)) or isinstance(op, str):
        op = (op, )
    test_op = f"rc.ORDEM_PRODUCAO IN ({', '.join(map(str, op))})"

    sql = f"""
        SELECT
          rc.ORDEM_PRODUCAO op
        , ro.NOTA_FISCAL_ENT nf
        , ro.SERI_FISCAL_ENT serie
        , ro.FORNECEDOR_CGC9 cnpj9
        , ro.FORNECEDOR_CGC4 cnpj4
        , ro.FORNECEDOR_CGC2 cnpj2
        , ro.PANOACAB_NIVEL99 nivel
        , ro.PANOACAB_GRUPO ref
        , ro.PANOACAB_SUBGRUPO tam
        , ro.PANOACAB_ITEM cor
        , sum(rc.QTDE_KG_FINAL) qtd
        FROM PCPT_020 ro -- cadastro de rolos
        LEFT JOIN PCPT_025 rc -- alocação de rolo para OP
          ON rc.CODIGO_ROLO = ro.CODIGO_ROLO
        WHERE {test_op}
          AND ro.NOTA_FISCAL_ENT > 0
        GROUP BY 
          rc.ORDEM_PRODUCAO
        , ro.NOTA_FISCAL_ENT
        , ro.SERI_FISCAL_ENT
        , ro.FORNECEDOR_CGC9
        , ro.FORNECEDOR_CGC4
        , ro.FORNECEDOR_CGC2
        , ro.PANOACAB_NIVEL99
        , ro.PANOACAB_GRUPO
        , ro.PANOACAB_SUBGRUPO
        , ro.PANOACAB_ITEM
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
