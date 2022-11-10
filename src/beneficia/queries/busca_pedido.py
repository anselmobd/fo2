from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import lm

__all__ = ['query']


def query(
    cursor,
    emissao_de=None,
    emissao_ate=None,
    empresa=2,
):

    filtra_emissao_de = lm(f"""\
        AND ped.DATA_EMIS_VENDA >= DATE '{emissao_de}' \
    """) if emissao_de else ''

    filtra_emissao_ate = lm(f"""\
        AND ped.DATA_EMIS_VENDA <= DATE '{emissao_ate}' \
    """) if emissao_ate else ''

    sql = lm(f'''
        SELECT
          ped.PEDIDO_VENDA PEDIDO
        , ped.DATA_EMIS_VENDA DT_EMISSAO
        , ped.OBSERVACAO OBS
        , CASE WHEN nfe.DOCUMENTO IS NULL
          THEN nf.NUM_NOTA_FISCAL
          ELSE NULL
          END NF
        FROM PEDI_100 ped -- pedido de venda
        LEFT JOIN FATU_050 nf -- capa de NF
          ON nf.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND nf.SITUACAO_NFISC = 1 -- Nota Emitida
        LEFT JOIN OBRF_010 nfe -- nota fiscal de entrada/devolução
          ON nfe.NOTA_DEV = nf.NUM_NOTA_FISCAL
         AND nfe.SITUACAO_ENTRADA in (1, 4) -- Nota Emitida, Nota de Fornecedor
        WHERE 1=1
          AND ped.CODIGO_EMPRESA = {empresa}
          {filtra_emissao_de} -- filtra_emissao_de
          {filtra_emissao_ate} -- filtra_emissao_ate
        ORDER BY
          ped.PEDIDO_VENDA
    ''')

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    return dados
