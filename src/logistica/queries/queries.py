from django.db import connections

from utils.functions.models.dictlist import dictlist, dictlist_lower


def get_nf_pela_chave(cursor, chave):
    sql = """
        SELECT
          f.NUM_NOTA_FISCAL
        FROM FATU_050 f
        WHERE f.CODIGO_EMPRESA = 1
          AND f.NUMERO_DANF_NFE = %s
          AND f.NUMERO_CAIXA_ECF = 0
    """
    cursor.execute(sql, [chave])
    return dictlist(cursor)


def get_chave_pela_nf(cursor, nf):
    sql = """
        SELECT
          f.NUMERO_DANF_NFE
        FROM FATU_050 f
        WHERE f.CODIGO_EMPRESA = 1
          AND f.NUM_NOTA_FISCAL = %s
          AND f.NUMERO_CAIXA_ECF = 0
    """
    cursor.execute(sql, [nf])
    return dictlist(cursor)
