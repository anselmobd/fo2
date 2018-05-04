from django.db import models

from fo2.models import rows_to_dict_list_lower


def inconsistencias_detalhe(cursor, op, ocs, est63=False):
    ocs_str = ''
    ocs_sep = ''
    for oc in ocs:
        ocs_str += ocs_sep + oc
        ocs_sep = ', '

    if est63:
        filtro_est63 = 'WHERE i.EST = 63'
    else:
        filtro_est63 = 'WHERE i.EST <> 63'

    sql = '''
        SELECT
          CASE WHEN i.SEQ = 0 THEN 99
          ELSE i.SEQ END SEQ
        , i.OC
        , i.OP
        , i.PERIODO
        , i.EST
        , i.QTD
        FROM (
          SELECT
            e.OC
          , e.OP
          , e.PERIODO
          , MAX(e.SEQ) SEQ
          , MAX(e.EST) EST
          , MAX(e.QTD) QTD
          FROM (
            SELECT
              le.SEQUENCIA_ESTAGIO SEQ
            , le.ORDEM_CONFECCAO OC
            , le.ORDEM_PRODUCAO OP
            , le.PERIODO_PRODUCAO PERIODO
            , le.CODIGO_ESTAGIO EST
            , le.QTDE_EM_PRODUCAO_PACOTE QTD
            FROM PCPC_040 le -- lote estágio atual
            WHERE le.QTDE_EM_PRODUCAO_PACOTE <> 0
              AND le.ORDEM_PRODUCAO = {op}
              AND le.ORDEM_CONFECCAO IN (
              {ocs}
              )
            UNION
            SELECT DISTINCT
              0 SEQ
            , le.ORDEM_CONFECCAO OC
            , le.ORDEM_PRODUCAO OP
            , le.PERIODO_PRODUCAO PERIODO
            , 0 EST
            , 0 QTD
            FROM PCPC_040 le -- lote estágio atual
            WHERE le.QTDE_EM_PRODUCAO_PACOTE = 0
              AND le.ORDEM_PRODUCAO = {op}
              AND le.ORDEM_CONFECCAO IN (
              {ocs}
              )
          ) e
          GROUP BY
            e.OC
          , e.OP
          , e.PERIODO
        ) i
        {filtro_est63}-- WHERE i.EST <> 63
        ORDER BY
          1
        , 2
    '''.format(op=op, ocs=ocs_str, filtro_est63=filtro_est63)
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
