import datetime

from fo2.models import rows_to_dict_list_lower


def item_no_tempo(
        cursor, ref, tam, cor, deposito):

    filtro_ref = ''
    if ref is not None and ref != '':
        filtro_ref = "AND t.GRUPO_ESTRUTURA = '{ref}'".format(ref=ref)

    filtro_tam = ''
    if tam is not None and tam != '':
        filtro_tam = "AND t.SUBGRUPO_ESTRUTURA = '{tam}'".format(tam=tam)

    filtro_cor = ''
    if cor is not None and cor != '':
        filtro_cor = "AND t.ITEM_ESTRUTURA = '{cor}'".format(cor=cor)

    filtro_deposito = ''
    if deposito is not None and deposito != '':
        filtro_deposito = "AND t.CODIGO_DEPOSITO = '{deposito}'".format(
            deposito=deposito)

    sql = f'''
        SELECT
          t.DATA_INSERCAO DATA
        , CASE WHEN t.ENTRADA_SAIDA = 'S' THEN
            -t.QUANTIDADE
          ELSE t.QUANTIDADE
          END QTD_SINAL
        , t.ENTRADA_SAIDA ES
        , t.QUANTIDADE QTD
        , t.NUMERO_DOCUMENTO DOC
        , t.PROCESSO_SYSTEXTIL PROC
        , t.USUARIO_SYSTEXTIL USUARIO
        , t.CNPJ_9
        , t.CNPJ_4
        , t.CNPJ_2
        , c.NOME_CLIENTE CLIENTE
        FROM ESTQ_300_ESTQ_310 t
        JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = t.CNPJ_9
         AND c.CGC_4 = t.CNPJ_4
        WHERE t.NIVEL_ESTRUTURA = 1
          {filtro_deposito} -- AND t.CODIGO_DEPOSITO = 101
          {filtro_ref} -- AND t.GRUPO_ESTRUTURA = '02156'
          {filtro_tam} -- AND t.SUBGRUPO_ESTRUTURA = 'P'
          {filtro_cor} -- AND t.ITEM_ESTRUTURA = '0000BR'
        ORDER BY
          t.DATA_INSERCAO DESC
    '''
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
