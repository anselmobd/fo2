from pprint import pprint

from utils.functions.format import format_cnpj
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(
    cursor,
    empresa=None,
    nf=None,
):
    filtra_nf = f"""--
        AND cnfe.DOCUMENTO = {nf}
    """ if nf else ''
    filtra_empresa = f"""--
        AND cnfe.LOCAL_ENTREGA = {empresa} -- empresa 1: matriz
    """ if empresa else ''

    sql = f"""
        SELECT DISTINCT  
          cnfe.DATA_TRANSACAO dt
        , cnfe.CGC_CLI_FOR_9 forn_cnpj9
        , cnfe.CGC_CLI_FOR_4 forn_cnpj4
        , cnfe.CGC_CLI_FOR_2 forn_cnpj2
        , COALESCE(forn.NOME_FANTASIA, forn.NOME_FORNECEDOR) forn_nome
        , cnfe.LOCAL_ENTREGA empr
        , cnfe.DOCUMENTO nf_num
        , cnfe.SERIE nf_ser
        , cnfe.NATOPER_NAT_OPER nat_op
        , cnfe.NATOPER_EST_OPER nat_uf
        , nat.COD_NATUREZA nat_cod
        , nat.OPERACAO_FISCAL nat_of
        , nat.DESCR_NAT_OPER nat_descr
        , cnfe.CODIGO_TRANSACAO tran_est
        , trest.DESCRICAO tran_descr
        , cnfe.HISTORICO_CONT hist_cont
        , histc.HISTORICO_CONTAB hist_descr
        --, infe.CODITEM_NIVEL99 niv
        --, infe.CODITEM_GRUPO ref
        --, infe.CODITEM_SUBGRUPO tam
        --, infe.CODITEM_ITEM cor
        --, infe.QUANTIDADE qtd
        FROM OBRF_010 cnfe -- capa de nota de entrada
        LEFT JOIN OBRF_015 infe -- item de nota de entrada
          ON infe.CAPA_ENT_FORCLI9 = cnfe.CGC_CLI_FOR_9
         AND infe.CAPA_ENT_FORCLI4 = cnfe.CGC_CLI_FOR_4
         AND infe.CAPA_ENT_FORCLI2 = cnfe.CGC_CLI_FOR_2
         AND infe.CAPA_ENT_NRDOC = cnfe.DOCUMENTO
         AND infe.CAPA_ENT_SERIE = cnfe.SERIE
        LEFT JOIN SUPR_010 forn -- fornecedor
          ON forn.FORNECEDOR9 = cnfe.CGC_CLI_FOR_9
         AND forn.FORNECEDOR4 = cnfe.CGC_CLI_FOR_4
         AND forn.FORNECEDOR2 = cnfe.CGC_CLI_FOR_2
        LEFT JOIN PEDI_080 nat -- natureza de operação
          ON nat.NATUR_OPERACAO = cnfe.NATOPER_NAT_OPER
         AND nat.ESTADO_NATOPER = cnfe.NATOPER_EST_OPER
        LEFT JOIN ESTQ_005 trest -- transação de estoque
          ON trest.CODIGO_TRANSACAO = cnfe.CODIGO_TRANSACAO
        LEFT JOIN CONT_010 histc -- histórico contabil
          ON histc.CODIGO_HISTORICO = cnfe.HISTORICO_CONT
        WHERE 1=1
          {filtra_empresa} -- filtra_empresa
          {filtra_nf} -- filtra_nf
          AND cnfe.SITUACAO_ENTRADA = 4 -- 4 = nota fornecedor
          AND cnfe.DATA_TRANSACAO >= DATE '2022-06-01'
          AND infe.CODITEM_NIVEL99 = 2
        ORDER BY 
          cnfe.DATA_TRANSACAO
        , cnfe.CGC_CLI_FOR_9
        , cnfe.CGC_CLI_FOR_4
        , cnfe.DOCUMENTO
        , cnfe.SERIE
    """
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    for row in data:
        row['dt'] = row['dt'].date()
        row['forn_cnpj'] = format_cnpj(row) if row['forn_cnpj9'] else '-'
        row['forn_cnpj_nome'] = f"{row['forn_cnpj']} {row['forn_nome']}"
        row['nf'] = f"{row['nf_num']}-{row['nf_ser']}" if row['nf_num'] else '-'
    return data