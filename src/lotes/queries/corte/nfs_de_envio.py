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
):
    filtra_dt_de = f"""--
        AND cnf.DATA_EMISSAO >= DATE '{dt_de}'
    """ if dt_de else ''
    filtra_dt_ate = f"""--
        AND cnf.DATA_EMISSAO <= DATE '{dt_ate}'
    """ if dt_ate else ''
    filtra_relacionado = f"""--
        AND cnfe.DOCUMENTO IS {'NOT' if relacionado else ''} NULL
    """ if relacionado is not None else ''
    sql = f"""
        SELECT DISTINCT
          cnf.NUM_NOTA_FISCAL nf_num
        , cnf.SERIE_NOTA_FISC nf_ser
        , cnf.VALOR_ITENS_NFIS valor
        , cnf.DATA_EMISSAO dt_emi
        , cnfe.CGC_CLI_FOR_9 nfe_cnpj9
        , cnfe.CGC_CLI_FOR_4 nfe_cnpj4
        , cnfe.CGC_CLI_FOR_2 nfe_cnpj2
        , cnfe.DOCUMENTO nfe_num
        , cnfe.SERIE nfe_ser
        , cnfe.VALOR_ITENS nfe_valor
        , cnfe.DATA_EMISSAO nfe_dt_emi
        FROM FATU_050 cnf -- capa faturamento
        LEFT JOIN OBRF_010 cnfe -- capa de nota de entrada
          ON cnfe.LOCAL_ENTREGA = cnf.CODIGO_EMPRESA
         AND cnfe.TUSSOR_ENVIA_NF = cnf.NUM_NOTA_FISCAL
        JOIN FATU_052 mf -- mensagem faturamento
          ON mf.NUM_NOTA = cnf.NUM_NOTA_FISCAL
        JOIN FATU_060 inf
          ON inf.CH_IT_NF_CD_EMPR  = cnf.CODIGO_EMPRESA
         AND inf.CH_IT_NF_NUM_NFIS = cnf.NUM_NOTA_FISCAL
         AND inf.CH_IT_NF_SER_NFIS = cnf.SERIE_NOTA_FISC
        WHERE 1=1
          {filtra_dt_de} -- filtra_dt_de
          {filtra_dt_ate} -- filtra_dt_ate
          -- AND mf.DES_MENSAG_12 NOT LIKE 'Transf. Matriz-Filial da NF%'
          -- AND cnfe.DOCUMENTO IS NULL
          {filtra_relacionado} -- filtra_relacionado
          AND cnf.CODIGO_EMPRESA = 1
          AND cnf.NATOP_NF_NAT_OPER = 301
          AND cnf.NATOP_NF_EST_OPER = 'RJ'
          AND cnf.CGC_9 = 7681643
          AND cnf.CGC_4 = 2
          AND cnf.CGC_2 = 78
          AND cnf.DATA_EMISSAO > DATE '2022-03-18'
          AND inf.NIVEL_ESTRUTURA = 2
        ORDER BY
          cnf.NUM_NOTA_FISCAL DESC
    """
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    for row in data:
        row['dt_emi'] = row['dt_emi'].date()
        row['nf'] = f"{row['nf_num']}-{row['nf_ser']}" if row['nf_num'] else "-"

        if row['nfe_num']:
            row['nfe_cnpj_num'] = format_cnpj(row)
            row['nfe_nf'] = f"{row['nfe_num']}-{row['nfe_ser']}"
            row['nfe_dt_emi'] = row['nfe_dt_emi'].date()
        else:
            row['nfe_cnpj_num'] = "-"
            row['nfe_nf'] = "-"
            row['nfe_dt_emi'] = "-"
            row['nfe_valor'] = "-"
    return data
