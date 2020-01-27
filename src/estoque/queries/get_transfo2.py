import datetime

from utils.models import rows_to_dict_list_lower


def get_transfo2(
        cursor, dep, numdoc=None, ref=None, cor=None, tam=None):

    filtro_dep = ''
    if dep is not None:
        filtro_dep = '''--
            AND t.CODIGO_DEPOSITO = {}
        '''.format(dep)

    filtro_numdoc = ''
    if numdoc is not None:
        filtro_numdoc = '''--
            AND t.NUMERO_DOCUMENTO = {}
        '''.format(numdoc)

    filtro_ref = ''
    if ref is not None:
        filtro_ref = '''--
            AND t.GRUPO_ESTRUTURA = '{}'
        '''.format(ref)

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

    sql = '''
        SELECT
          t.CODIGO_DEPOSITO DEP
        , t.NUMERO_DOCUMENTO NUMDOC
        , count(*)
        FROM ESTQ_300 t
        WHERE t.NIVEL_ESTRUTURA = 1
          AND t.NUMERO_DOCUMENTO >= 702000000
          AND t.NUMERO_DOCUMENTO <= 702999999
          {filtro_dep} -- filtro_dep
          {filtro_numdoc} -- filtro_numdoc
          {filtro_ref} -- filtro_ref
          {filtro_cor} -- filtro_cor
          {filtro_tam} -- filtro_tam
        GROUP BY
          t.CODIGO_DEPOSITO
        , t.NUMERO_DOCUMENTO
        ORDER BY
          t.CODIGO_DEPOSITO
        , t.NUMERO_DOCUMENTO DESC
    '''.format(
        filtro_dep=filtro_dep,
        filtro_numdoc=filtro_numdoc,
        filtro_ref=filtro_ref,
        filtro_cor=filtro_cor,
        filtro_tam=filtro_tam,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
