from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import lms

__all__ = ['query']


def query(
    cursor,
    empresa=2,
    emissao_de=None,
    emissao_ate=None,
    faturado=None,
    obs=None,
):

    filtra_emissao_de = lms(f"""\
        AND ped.DATA_EMIS_VENDA >= DATE '{emissao_de}'
    """) if emissao_de else ''

    filtra_emissao_ate = lms(f"""\
        AND ped.DATA_EMIS_VENDA <= DATE '{emissao_ate}' 
    """) if emissao_ate else ''

    filtra_faturado = ''
    if faturado is not None:
        if faturado:
            filtra_faturado = lms("""\
                AND nf.NUM_NOTA_FISCAL IS NOT NULL 
                AND nfe.DOCUMENTO IS NULL 
            """)
        else:
            filtra_faturado = lms("""\
                AND (
                  nf.NUM_NOTA_FISCAL IS NULL 
                  OR nfe.DOCUMENTO IS NOT NULL 
                )
            """)

    # filtra_obs = lms(f"""\
    #     AND ped.OBSERVACAO LIKE '%{obs}%' 
    # """) if obs else ''

    sql = lms(f"""\
        SELECT
          ped.PEDIDO_VENDA PEDIDO
        , ped.DATA_EMIS_VENDA DT_EMISSAO
        , ped.OBSERVACAO OBS
        , CASE WHEN nfe.DOCUMENTO IS NULL
          THEN nf.NUM_NOTA_FISCAL
          ELSE NULL
          END NF
        , nf.DATA_EMISSAO DT_NF
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
          {filtra_faturado} -- filtra_faturado
          -- filtra_obs -- filtra_obs
        ORDER BY
          ped.PEDIDO_VENDA
    """)

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        if not row['nf']:
            row['dt_nf'] = None
        if row['dt_nf']:
            row['dt_nf'] = row['dt_nf'].date()

    if obs:
        return [
            row for row in dados
            if row['obs'] and obs.casefold() in row['obs'].casefold()
        ]

    return dados
