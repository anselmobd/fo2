from pprint import pprint

from utils.functions.models import (
    GradeQtd,
    rows_to_dict_list_lower,
)


def sql_calc_modelo(field):
    return f'''--
          TRIM(
            LEADING '0' FROM (
              REGEXP_REPLACE(
                {field},
                '^[abAB]?([0-9]+)[a-zA-Z]*$',
                '\\1'
              )
            )
          )
    '''


def sql_filtra_modelo(field, modelo, conector='AND'):
    if field is None or field == '':
        return ''
    if modelo is None or modelo == '':
        return ''
    return f'''--
        {conector} {sql_calc_modelo(field)} = '{modelo}'
    '''


def sql_filtra_deposito(field, deposito, conector='AND'):
    if deposito is None or deposito == '':
        return ''
    if type(deposito) is tuple:
        lista = ", ".join(map(str, deposito))
        return f"{conector} {field} IN ({lista})"
    else:
        return f"{conector} {field} = '{dep}'"


def total_modelo_deposito(cursor, modelo, deposito):

    filtro_modelo = sql_filtra_modelo(
        'e.CDITEM_GRUPO',
        modelo,
    )

    filtro_deposito = sql_filtra_deposito(
        'e.DEPOSITO',
        deposito,
    )

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
    dados = rows_to_dict_list_lower(cursor)
    row = dados[0]
    return row['quantidade']
