from django.db import connections

from fo2.models import rows_to_dict_list, rows_to_dict_list_lower


def get_nf_pela_chave(cursor, chave):
    sql = """
        SELECT
          f.NUM_NOTA_FISCAL
        FROM FATU_050 f
        WHERE f.CODIGO_EMPRESA = 1
          AND f.NUMERO_DANF_NFE = %s
    """
    cursor.execute(sql, [chave])
    return rows_to_dict_list(cursor)


def get_chave_pela_nf(cursor, nf):
    sql = """
        SELECT
          f.NUMERO_DANF_NFE
        FROM FATU_050 f
        WHERE f.CODIGO_EMPRESA = 1
          AND f.NUM_NOTA_FISCAL = %s
    """
    cursor.execute(sql, [nf])
    return rows_to_dict_list(cursor)
