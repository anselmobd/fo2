from utils.functions.models import rows_to_dict_list_lower


def get_estoque_dep_ref_cor_tam(cursor, deposito, ref, cor, tam):
    sql = '''
        SELECT
          e.QTDE_ESTOQUE_ATU ESTOQUE
        FROM ESTQ_040 e
        WHERE 1=1
          AND e.CDITEM_NIVEL99 = 1
          AND e.CDITEM_GRUPO = '{ref}'
          AND e.CDITEM_SUBGRUPO = '{tam}'
          AND e.CDITEM_ITEM = '{cor}'
          AND e.DEPOSITO = {deposito}
    '''.format(
        deposito=deposito,
        ref=ref,
        cor=cor,
        tam=tam,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
