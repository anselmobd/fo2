from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def busca_modelo(cursor, descricao=None):
    if descricao is None:
        descricao = ''

    filtro_descricao = ''
    if descricao != '':
        filtro_descricao = '''
            AND r.DESCR_REFERENCIA LIKE '%{}%'
        '''.format(descricao)

    sql = """
        SELECT DISTINCT
          TO_NUMBER(
            TRIM(
              LEADING '0' FROM (
                REGEXP_REPLACE(
                  r.REFERENCIA, '[^0-9]', ''
                )
              )
            )
          ) MODELO
        --, r.REFERENCIA REF
        , MAX(r.DESCR_REFERENCIA) DESCR
        FROM BASI_030 r -- ref
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.DESCR_REFERENCIA NOT LIKE '-%'
          AND r.REFERENCIA < 'C0000'
          {filtro_descricao} -- filtro_descricao
        GROUP BY
          TO_NUMBER(
            TRIM(
              LEADING '0' FROM (
                REGEXP_REPLACE(
                  r.REFERENCIA, '[^0-9]', ''
                )
              )
            )
          )
        --, r.REFERENCIA
        ORDER BY
          1
    """.format(
        filtro_descricao=filtro_descricao,
    )
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
