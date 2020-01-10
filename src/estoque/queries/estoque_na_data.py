import datetime

from fo2.models import rows_to_dict_list_lower


def estoque_na_data(cursor, data=None, hora=None, deposito=None):

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
          0 QTD
        FROM DUAL
    '''
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
