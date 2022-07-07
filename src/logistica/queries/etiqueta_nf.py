from django.db import connections

from utils.functions.format import format_cnpj
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
        , COALESCE(ped.COD_PED_CLIENTE, ' ') ped_cli
        , c.CGC_9
        , c.CGC_4
        , c.CGC_2
        , c.NOME_CLIENTE cli_nome
        , c.FANTASIA_CLIENTE cli_fant
        FROM FATU_050 f -- capa de nota fiscal de saída
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = f.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada 
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = f.PEDIDO_VENDA
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
         AND c.CGC_2 = ped.CLI_PED_CGC_CLI2
        WHERE f.CODIGO_EMPRESA = 1 -- empresa tussor
          AND f.NUM_NOTA_FISCAL = {nf}
          AND f.NUMERO_CAIXA_ECF = 0 -- não é nota especial
          AND f.SITUACAO_NFISC IN (1, 4) -- ativa
          AND f.COD_STATUS = 100 -- foi aceita pela receita
          AND fe.SITUACAO_ENTRADA IS NULL -- devolução não existente
    """
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    for row in data:
        row['cli_cnpj_num'] = format_cnpj(row, sep=False)
        row['cli_cnpj'] = format_cnpj(row)
        row['cli_cnpj_nome'] = f"{row['cli_cnpj']} {row['cli_nome']}"
    return data
