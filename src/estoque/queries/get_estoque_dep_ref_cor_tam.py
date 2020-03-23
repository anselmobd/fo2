from utils.functions.models import rows_to_dict_list_lower


def get_estoque_dep_niv_ref_cor_tam(cursor, deposito, niv, ref, cor, tam):
    sql = f'''
        SELECT
          e.QTDE_ESTOQUE_ATU ESTOQUE
        FROM ESTQ_040 e
        WHERE 1=1
          AND e.CDITEM_NIVEL99 = {niv}
          AND e.CDITEM_GRUPO = '{ref}'
          AND e.CDITEM_SUBGRUPO = '{tam}'
          AND e.CDITEM_ITEM = '{cor}'
          AND e.DEPOSITO = {deposito}
    '''
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def get_estoque_dep_ref_cor_tam(cursor, deposito, ref, cor, tam):
    return get_estoque_dep_niv_ref_cor_tam(cursor, deposito, 1, ref, cor, tam)
