import time
from pprint import pprint

from django.core.cache import cache

from utils.cache import entkeys
from utils.functions import my_make_key_cache, fo2logger
from utils.functions.models import (
    GradeQtd,
    rows_to_key_dict,
    rows_to_dict_list_lower,
)
from utils.functions.queries import sql_where, sql_where_none_if


def sql_calc_modelo_de_ref(field=""):
    if field:
        return f"""--
            TRIM(
                LEADING '0' FROM (
                REGEXP_REPLACE(
                    {field},
                    '^[a-zA-Z]?([0-9]+)[a-zA-Z]*$',
                    '\\1'
                )
                )
            )
        """
    return ""


def sql_where_modelo_de_ref(field, modelo, operation="=", conector="AND"):
    return sql_where(
        sql_calc_modelo_de_ref(field),
        str(modelo),
        operation=operation,
        conector=conector,
    )


def sql_filtra_modelo(field, modelo, conector='AND'):
    if modelo is None or modelo == '':
        return ''
    if type(modelo) is list:
        lista = ", ".join([f"'{d}'" for d in map(str, modelo)])
        return f"{conector} {field} IN ({lista})"
    else:
        return f"{conector} {field} = '{modelo}'"


def totais_modelos_depositos(cursor, deposito, modelos=None):

    key_cache = my_make_key_cache(
        'totais_modelos_depositos', deposito)

    while True:
        cached_result = cache.get(key_cache)
        if cached_result is not None:
            fo2logger.info('cached '+key_cache)
            return cached_result

        if cache.get(f"{key_cache}_calc_"):
            time.sleep(0.2)
        else:
            cache.set(f"{key_cache}_calc_", "c", timeout=entkeys._SECOND * 5)
            break

    filtro_deposito = sql_where_none_if(
        'e.DEPOSITO', deposito, '', operation="IN")

    calc_modelo = sql_calc_modelo_de_ref('e.CDITEM_GRUPO')

    filtro_modelo = sql_filtra_modelo(
        f'{calc_modelo}',
        modelos,
    )

    sql = f'''
        SELECT
          {calc_modelo} MODELO
        , SUM(e.QTDE_ESTOQUE_ATU) QUANTIDADE
        FROM ESTQ_040 e
        WHERE 1=1 -- e.LOTE_ACOMP = 0
          AND e.CDITEM_NIVEL99 = 1
          {filtro_deposito} -- filtro_deposito
          {filtro_modelo} -- filtro_modelo
        GROUP BY
          {calc_modelo}
        ORDER BY
          1
    '''

    cursor.execute(sql)
    cached_result = rows_to_key_dict(cursor, 'MODELO')

    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result


def total_modelo_deposito(cursor, modelo, deposito):

    filtro_modelo = sql_where_modelo_de_ref(
        'e.CDITEM_GRUPO',
        modelo,
    )

    filtro_deposito = sql_where_none_if(
        'e.DEPOSITO', deposito, '', operation="IN")

    sql = f'''
        SELECT
          SUM(e.QTDE_ESTOQUE_ATU) QUANTIDADE
        FROM ESTQ_040 e
        WHERE 1=1 -- e.LOTE_ACOMP = 0
          AND e.CDITEM_NIVEL99 = 1
          {filtro_modelo} -- filtro_modelo
          {filtro_deposito} -- filtro_deposito
    '''

    cursor.execute(sql)
    row = cursor.fetchone()
    return row[0]
