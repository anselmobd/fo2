from utils.functions.models import rows_to_dict_list_lower


def refs_com_movimento(cursor, data_ini=None):
    filtro_data_ini = ''
    if data_ini is not None:
        filtro_data_ini = (
            "AND ee.DATA_MOVIMENTO >= "
            "TO_DATE('{data_ini}', 'yyyy-mm-dd')".format(data_ini=data_ini)
        )

    sql = '''
        SELECT DISTINCT
          ee.GRUPO_ESTRUTURA REF
        FROM ESTQ_300_ESTQ_310 ee
        WHERE ee.NIVEL_ESTRUTURA = 1
          AND ee.GRUPO_ESTRUTURA < 'C0000'
          AND ee.CODIGO_DEPOSITO IN (231, 101, 102)
          {filtro_data_ini} -- filtro_data_ini
        ORDER BY
          ee.GRUPO_ESTRUTURA
    '''.format(
        filtro_data_ini=filtro_data_ini,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
