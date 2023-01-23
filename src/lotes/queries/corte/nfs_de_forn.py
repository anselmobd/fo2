from pprint import pprint

from utils.functions.format import format_cnpj
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(
    cursor,
    dt_de=None,
    dt_ate=None,
    relacionado=None,
    item_nivel=2,
    empr=None,
    nf_num=None,
    nf_ser=None,
    cnpj9=None,
):
    filtra_dt_de = f"""--
        AND cnfe.DATA_EMISSAO >= DATE '{dt_de}'
    """ if dt_de else ''
    filtra_dt_ate = f"""--
        AND cnfe.DATA_EMISSAO <= DATE '{dt_ate}'
    """ if dt_ate else ''
    filtra_relacionado = f"""--
        AND cnfe.TUSSOR_ENVIA_NF {'<>' if relacionado else '='} 0
    """ if relacionado is not None else ''
    filtra_item_nivel = f"""--
        AND infe.CODITEM_NIVEL99 = {item_nivel}
    """ if item_nivel is not None else ''
    filtra_empr = f"""--
        AND cnfe.LOCAL_ENTREGA = '{empr}'
    """ if empr is not None else ''
    filtra_nf_num = f"""--
        AND cnfe.DOCUMENTO = {nf_num}
    """ if nf_num is not None else ''
    filtra_nf_ser = f"""--
        AND cnfe.SERIE = {nf_ser}
    """ if nf_ser is not None else ''
    filtra_cnpj9 = f"""--
        AND cnfe.CGC_CLI_FOR_9 = {cnpj9}
    """ if cnpj9 is not None else ''
    sql = f"""
        SELECT DISTINCT
          cnfe.LOCAL_ENTREGA empr
        , cnfe.CGC_CLI_FOR_9 cnpj9
        , cnfe.CGC_CLI_FOR_4 cnpj4
        , cnfe.CGC_CLI_FOR_2 cnpj2
        , cnfe.DOCUMENTO nf_num
        , cnfe.SERIE nf_ser
        , cnfe.VALOR_ITENS valor
        , cnfe.DATA_TRANSACAO dt_trans
        , cnfe.DATA_EMISSAO dt_emi
        , cnfe.DATA_DIGITACAO dt_dig
        , cnfe.TUSSOR_ENVIA_NF nf_envia
        , COALESCE(forn.NOME_FANTASIA, forn.NOME_FORNECEDOR) forn_nome
        , cnf.VALOR_ITENS_NFIS nf_env_valor
        , cnf.DATA_EMISSAO nf_env_dt_emi
        , ( SELECT
              LISTAGG(
                DISTINCT
                '(' ||
                infe.CODITEM_NIVEL99 || '.' ||
                infe.CODITEM_GRUPO || ')' ||
                r.DESCR_REFERENCIA
              , ', '
              )
              WITHIN GROUP (ORDER BY infe.CODITEM_NIVEL99, infe.CODITEM_GRUPO)
            FROM OBRF_015 infe
            LEFT JOIN basi_030 r
              ON r.NIVEL_ESTRUTURA = infe.CODITEM_NIVEL99
             AND r.REFERENCIA = infe.CODITEM_GRUPO
            WHERE infe.CAPA_ENT_FORCLI9 = cnfe.CGC_CLI_FOR_9
              AND infe.CAPA_ENT_FORCLI4 = cnfe.CGC_CLI_FOR_4
              AND infe.CAPA_ENT_FORCLI2 = cnfe.CGC_CLI_FOR_2
              AND infe.CAPA_ENT_NRDOC = cnfe.DOCUMENTO
              AND infe.CAPA_ENT_SERIE = cnfe.SERIE
          ) itens
        FROM OBRF_010 cnfe -- capa de nota de entrada
        LEFT JOIN SUPR_010 forn -- fornecedor
          ON forn.FORNECEDOR9 = cnfe.CGC_CLI_FOR_9
         AND forn.FORNECEDOR4 = cnfe.CGC_CLI_FOR_4
         AND forn.FORNECEDOR2 = cnfe.CGC_CLI_FOR_2
        LEFT JOIN FATU_050 cnf -- capa faturamento de envio
          ON cnf.CODIGO_EMPRESA = cnfe.LOCAL_ENTREGA
         AND cnf.NUM_NOTA_FISCAL = cnfe.TUSSOR_ENVIA_NF
         AND cnf.SERIE_NOTA_FISC = 1
        LEFT JOIN OBRF_015 infe -- item de nota de entrada
          ON infe.CAPA_ENT_FORCLI9 = cnfe.CGC_CLI_FOR_9
         AND infe.CAPA_ENT_FORCLI4 = cnfe.CGC_CLI_FOR_4
         AND infe.CAPA_ENT_FORCLI2 = cnfe.CGC_CLI_FOR_2
         AND infe.CAPA_ENT_NRDOC = cnfe.DOCUMENTO
         AND infe.CAPA_ENT_SERIE = cnfe.SERIE
        WHERE 1=1
          {filtra_dt_de} -- filtra_dt_de
          {filtra_dt_ate} -- filtra_dt_ate
          {filtra_relacionado} -- filtra_relacionado
          {filtra_empr} -- filtra_empr
          {filtra_nf_num} -- filtra_nf_num
          {filtra_nf_ser} -- filtra_nf_ser
          {filtra_cnpj9} -- filtra_cnpj9
          AND cnfe.LOCAL_ENTREGA = 1 -- empresa 1: matriz
          AND cnfe.SITUACAO_ENTRADA = 4 -- 4 = nota fornecedor
          AND cnfe.DATA_TRANSACAO >= DATE '2022-03-18'
          -- AND infe.CODITEM_NIVEL99 = 2
          {filtra_item_nivel} -- filtra_item_nivel
        ORDER BY
          cnfe.DATA_EMISSAO DESC
        , cnfe.CGC_CLI_FOR_9 DESC
        , cnfe.CGC_CLI_FOR_4 DESC
        , cnfe.DOCUMENTO DESC
        , cnfe.SERIE DESC
    """
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    for row in data:
        row['cnpj'] = format_cnpj(row)
        row['cnpj_num'] = format_cnpj(row, sep=False)
        row['forn_nome'] = f"{row['cnpj']} {row['forn_nome']}"
        row['dt_emi'] = row['dt_emi'].date()
        row['dt_dig'] = row['dt_dig'].date()
        row['nf'] = f"{row['nf_num']}-{row['nf_ser']}" if row['nf_num'] else "-"
        if row['nf_envia'] == 0:
            row['nf_envia'] = "-"
        if row['nf_env_valor'] is None:
            row['nf_env_valor'] = "-"
            row['nf_env_dt_emi'] = "-"
        else:
            row['nf_env_dt_emi'] = row['nf_env_dt_emi'].date()
    return data
