import collections.abc
from pprint import pprint

from utils.functions.format import format_cnpj
from utils.functions.queries import debug_cursor_execute
from utils.functions.models.dictlist import dictlist_lower


def query(cursor, op):
    if (not isinstance(op, collections.abc.Sequence)) or isinstance(op, str):
        op = (op, )
    filtra_op = f"""--
        AND rc.ORDEM_PRODUCAO IN ({', '.join(map(str, op))})
    """

    sql = f"""
        SELECT
          rc.ORDEM_PRODUCAO op
        , ro.NOTA_FISCAL_ENT nf_num
        , ro.SERI_FISCAL_ENT nf_ser
        , ro.FORNECEDOR_CGC9 cnpj9
        , ro.FORNECEDOR_CGC4 cnpj4
        , ro.FORNECEDOR_CGC2 cnpj2
        , ro.PANOACAB_NIVEL99 nivel
        , ro.PANOACAB_GRUPO ref
        , ro.PANOACAB_SUBGRUPO tam
        , ro.PANOACAB_ITEM cor
        , COALESCE(forn.NOME_FANTASIA, forn.NOME_FORNECEDOR) forn
        , i.NARRATIVA item_descr
        , count(*) rolos
        , sum(rc.QTDE_KG_FINAL) qtd
        FROM PCPT_020 ro -- cadastro de rolos
        LEFT JOIN PCPT_025 rc -- alocação de rolo para OP
          ON rc.CODIGO_ROLO = ro.CODIGO_ROLO
        LEFT JOIN SUPR_010 forn -- fornecedor
          ON forn.FORNECEDOR9 = ro.FORNECEDOR_CGC9
         AND forn.FORNECEDOR4 = ro.FORNECEDOR_CGC4
         AND forn.FORNECEDOR2 = ro.FORNECEDOR_CGC2
        LEFT JOIN BASI_010 i -- item
          ON i.NIVEL_ESTRUTURA = ro.PANOACAB_NIVEL99
         AND i.GRUPO_ESTRUTURA = ro.PANOACAB_GRUPO
         AND i.SUBGRU_ESTRUTURA = ro.PANOACAB_SUBGRUPO
         AND i.ITEM_ESTRUTURA = ro.PANOACAB_ITEM
        WHERE 1=1
          {filtra_op} -- filtra_op
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
        , forn.NOME_FANTASIA
        , forn.NOME_FORNECEDOR
        , i.NARRATIVA
    """
    debug_cursor_execute(cursor, sql)

    data = dictlist_lower(cursor)
    for row in data:
        row['nf'] = f"{row['nf_num']}-{row['nf_ser']}"
        row['item'] = f"{row['nivel']}.{row['ref']}.{row['tam']}.{row['cor']}"
        row['cnpj'] = format_cnpj(row)
        row['cnpj_num'] = format_cnpj(row, sep=False)
        row['cnpj_forn'] = f"{row['cnpj']} {row['forn']}"

    return data
