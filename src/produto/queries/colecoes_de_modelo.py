from fo2.models import rows_to_dict_list

import lotes.models


def colecoes_de_modelo(cursor, modelo):
    sql = """
        SELECT
          r.COLECAO
        FROM BASI_030 r -- item (ref+tam+cor)
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.REFERENCIA < 'C0000'
          AND r.DESCR_REFERENCIA NOT LIKE '-%'
          AND TRIM(LEADING '0' FROM (
                REGEXP_REPLACE(r.REFERENCIA, '[^0-9]', ''))) = {}
        GROUP BY
          r.COLECAO
    """.format(modelo)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def colecao_de_modelo(cursor, modelo):
    rows = colecoes_de_modelo(cursor, modelo)
    if len(rows) != 1:
        return -1
    return rows[0]['COLECAO']


def lead_de_modelo(cursor, modelo):
    lead = 0
    rows = colecoes_de_modelo(cursor, modelo)
    for row in rows:
        try:
            lc = lotes.models.LeadColecao.objects.get(colecao=row['COLECAO'])
            lc_lead = lc.lead
        except models.LeadColecao.DoesNotExist:
            lc_lead = 0
            break
        if lead == 0:
            lead = lc_lead
        else:
            if lead != lc_lead:
                lead = 0
                break
    return lead
