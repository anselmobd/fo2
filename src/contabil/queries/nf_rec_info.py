from pprint import pprint

from utils.functions.format import format_cnpj
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


situacao_entrada = {
    0: "Nota Calculada",
    1: "Nota Emitida",
    2: "Nota Cancelada",
    3: "Nota Incompleta",
    4: "Nota de Fornecedor",
    5: "Nota Incompleta",
}

def query(
    cursor,
    empresa=None,
    cnpj=None,
    nf=None,
    sit_entr=None,
    dt_de=None,
    dt_ate=None,
    niv=None,
    ref=None,
    tam=None,
    cor=None,
):
    filtra_empresa = f"""--
        AND cnfe.LOCAL_ENTREGA = {empresa}
    """ if empresa else ''
    filtra_cnpj9 = f"""--
        AND cnfe.CGC_CLI_FOR_9 = {cnpj[:8]}
    """ if cnpj and len(cnpj) >= 8 else ''
    filtra_cnpj4 = f"""--
        AND cnfe.CGC_CLI_FOR_4 = {cnpj[8:12]}
    """ if cnpj and len(cnpj) >= 12 else ''
    filtra_cnpj2 = f"""--
        AND cnfe.CGC_CLI_FOR_2 = {cnpj[12:14]}
    """ if cnpj and len(cnpj) >= 14 else ''
    filtra_nf = f"""--
        AND cnfe.DOCUMENTO = {nf}
    """ if nf else ''
    filtra_sit_entr = f"""--
        AND cnfe.SITUACAO_ENTRADA = {sit_entr}
    """ if sit_entr else ''
    filtra_dt_de = f"""--
        AND cnfe.DATA_TRANSACAO >= DATE '{dt_de}'
    """ if dt_de else ''
    filtra_dt_ate = f"""--
        AND cnfe.DATA_TRANSACAO <= DATE '{dt_ate}'
    """ if dt_ate else ''
    filtra_niv = f"""--
        AND infe.CODITEM_NIVEL99 = '{niv}'
    """ if niv else ''
    filtra_ref = f"""--
        AND infe.CODITEM_GRUPO = '{ref}'
    """ if ref else ''
    filtra_tam = f"""--
        AND infe.CODITEM_SUBGRUPO = '{tam}'
    """ if tam else ''
    filtra_cor = f"""--
        AND infe.CODITEM_ITEM = '{cor}'
    """ if cor else ''

    sql = f"""
        SELECT DISTINCT  
          cnfe.DATA_TRANSACAO dt_trans
        , cnfe.DATA_DIGITACAO dt_dig
        , cnfe.DATA_EMISSAO dt_emi
        , cnfe.CGC_CLI_FOR_9 forn_cnpj9
        , cnfe.CGC_CLI_FOR_4 forn_cnpj4
        , cnfe.CGC_CLI_FOR_2 forn_cnpj2
        , COALESCE(forn.NOME_FANTASIA, forn.NOME_FORNECEDOR) forn_nome
        , cnfe.LOCAL_ENTREGA empr
        , cnfe.DOCUMENTO nf_num
        , cnfe.SERIE nf_ser
        , cnfe.NATOPER_NAT_OPER nat_op
        , cnfe.NATOPER_EST_OPER nat_uf
        , cnfe.QTDE_ITENS 
        , cnfe.VALOR_ITENS
        , cnfe.SITUACAO_ENTRADA sit_entr
        , nat.COD_NATUREZA nat_cod
        , nat.OPERACAO_FISCAL nat_of
        , nat.DESCR_NAT_OPER nat_descr
        , cnfe.CODIGO_TRANSACAO tran_est
        , trest.DESCRICAO tran_descr
        , cnfe.HISTORICO_CONT hist_cont
        , histc.HISTORICO_CONTAB hist_descr
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
          {filtra_cnpj9} -- filtra_cnpj9
          {filtra_cnpj4} -- filtra_cnpj4
          {filtra_cnpj2} -- filtra_cnpj2
          {filtra_nf} -- filtra_nf
          {filtra_sit_entr} -- filtra_sit_entr
          {filtra_dt_de} -- filtra_dt_de
          {filtra_dt_ate} -- filtra_dt_ate
          {filtra_niv} -- filtra_niv
          {filtra_ref} -- filtra_ref
          {filtra_tam} -- filtra_tam
          {filtra_cor} -- filtra_cor
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
        row['dt_trans'] = row['dt_trans'].date()
        row['dt_dig'] = row['dt_dig'].date()
        row['dt_emi'] = row['dt_emi'].date()
        row['forn_cnpj_num'] = format_cnpj(row, sep=False) if row['forn_cnpj9'] else ''
        row['forn_cnpj'] = format_cnpj(row) if row['forn_cnpj9'] else '-'
        row['forn_cnpj_nome'] = f"{row['forn_cnpj']} {row['forn_nome']}"
        row['nf'] = f"{row['nf_num']}-{row['nf_ser']}" if row['nf_num'] else '-'
        row['nat'] = f"{row['nat_op']}-{row['nat_uf']}"
        row['cfop'] = f"{row['nat_cod']}{row['nat_of']}"
        row['sit_entr_descr'] = situacao_entrada[row['sit_entr']]
    return data
