from fo2.models import rows_to_dict_list_lower


def select_transacao_ajuste(
        cursor, deposito, ref, tam, cor, num_doc):
    sql = '''
        SELECT
          t.*
        FROM ESTQ_300 t
        WHERE t.NIVEL_ESTRUTURA = 1
          AND t.CODIGO_DEPOSITO = {deposito}
          AND t.GRUPO_ESTRUTURA = '{ref}'
          AND t.SUBGRUPO_ESTRUTURA = '{tam}'
          AND t.ITEM_ESTRUTURA = '{cor}'
          AND t.NUMERO_DOCUMENTO = {num_doc}
    '''.format(
        deposito=deposito,
        ref=ref,
        tam=tam,
        cor=cor,
        num_doc=num_doc,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
