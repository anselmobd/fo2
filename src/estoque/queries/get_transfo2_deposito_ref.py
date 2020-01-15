import datetime

from fo2.models import rows_to_dict_list_lower


def get_transfo2_deposito_ref(
        cursor, deposito, ref, cor=None, tam=None,
        tipo='f', data=None, hora=None):

    filtro_cor = ''
    if cor is not None:
        filtro_cor = '''--
            AND t.ITEM_ESTRUTURA = '{}'
        '''.format(cor)

    filtro_tam = ''
    if tam is not None:
        filtro_tam = '''--
            AND t.SUBGRUPO_ESTRUTURA = '{}'
        '''.format(tam)

    filtro_tipo = ''
    if tipo == 'f':  # fo2
        filtro_tipo = '''--
            AND t.NUMERO_DOCUMENTO >= 702000000
            AND t.NUMERO_DOCUMENTO <= 702999999
        '''
    elif tipo == 's':  # systextil
        filtro_tipo = '''--
            AND (  t.NUMERO_DOCUMENTO < 702000000
                OR t.NUMERO_DOCUMENTO > 702999999
                )
        '''

    filtro_data = ''
    if data is not None:
        if hora is None:
            data_hora = data
        else:
            data_hora = datetime.datetime.combine(data, hora)
        filtro_data = '''--
            AND t.DATA_INSERCAO >= TIMESTAMP '{}'
        '''.format(
            data_hora.strftime('%Y-%m-%d %H:%M:%S')
        )

    sql = '''
        SELECT
          t.DATA_INSERCAO HORA
        , t.NUMERO_DOCUMENTO NUMDOC
        , t.ITEM_ESTRUTURA COR
        , t.SUBGRUPO_ESTRUTURA TAM
        , t.CODIGO_TRANSACAO TRANS
        , t.ENTRADA_SAIDA ES
        , t.QUANTIDADE QTD
        FROM ESTQ_300_ESTQ_310 t
        WHERE t.CODIGO_DEPOSITO = '{deposito}'
          AND t.NIVEL_ESTRUTURA = '1'
          AND t.GRUPO_ESTRUTURA = '{ref}'
          {filtro_cor} -- filtro_cor
          {filtro_tam} -- filtro_tam
          {filtro_data} -- filtro_data
          {filtro_tipo} -- filtro_tipo
        ORDER BY
          t.DATA_INSERCAO DESC
    '''.format(
        deposito=deposito,
        ref=ref,
        filtro_cor=filtro_cor,
        filtro_tam=filtro_tam,
        filtro_data=filtro_data,
        filtro_tipo=filtro_tipo,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
