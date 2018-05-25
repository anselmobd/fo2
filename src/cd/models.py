from django.db import models

from fo2.models import rows_to_dict_list_lower, GradeQtd


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
        , i.REF
        , i.TAM
        , i.COR
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
          , e.REF
          , e.TAM
          , e.COR
          , MAX(e.SEQ) SEQ
          , MAX(e.EST) EST
          , MAX(e.QTD) QTD
          FROM (
            SELECT
              le.SEQUENCIA_ESTAGIO SEQ
            , le.ORDEM_CONFECCAO OC
            , le.ORDEM_PRODUCAO OP
            , le.PERIODO_PRODUCAO PERIODO
            , le.PROCONF_GRUPO REF
            , le.PROCONF_SUBGRUPO TAM
            , le.PROCONF_ITEM COR
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
            , le.PROCONF_GRUPO REF
            , le.PROCONF_SUBGRUPO TAM
            , le.PROCONF_ITEM COR
            , 0 EST
            , le.QTDE_PECAS_PROD QTD
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
          , e.REF
          , e.TAM
          , e.COR
        ) i
        {filtro_est63}-- WHERE i.EST <> 63
        ORDER BY
          1
        , i.REF
        , i.TAM
        , i.COR
        , i.OC
    '''.format(op=op, ocs=ocs_str, filtro_est63=filtro_est63)
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def grade_solicitacao(cursor, solicit_id, referencia):
    # Grade de solicitação
    grade = GradeQtd(
        cursor, [solicit_id, referencia])

    # tamanhos
    sql = '''
        SELECT distinct
          l.ordem_tamanho
        , l.tamanho
        from fo2_cd_solicita_lote_qtd s
        join fo2_cd_lote l
          on l.id = s.lote_id
        where s.solicitacao_id = %s
          and l.referencia = %s
        order by
          1
    '''
    grade.col(
        id='tamanho',
        name='Tamanho',
        total='Total',
        sql=sql
        )

    # cores
    sql = '''
        SELECT distinct
          l.cor
        from fo2_cd_solicita_lote_qtd sq
        join fo2_cd_lote l
          on l.id = sq.lote_id
        where sq.solicitacao_id = %s
          and l.referencia = %s
        order by
          1
    '''
    grade.row(
        id='cor',
        name='Cor',
        name_plural='Cores',
        total='Total',
        sql=sql
        )

    # sortimento
    sql = '''
        SELECT distinct
          l.tamanho
        , l.cor
        , sum(sq.qtd) qtd
        from fo2_cd_solicita_lote_qtd sq
        join fo2_cd_lote l
          on l.id = sq.lote_id
        where sq.solicitacao_id = %s
          and l.referencia = %s
        group by
          l.tamanho
        , l.cor
        order by
          l.tamanho
        , l.cor
    '''
    grade.value(
        id='qtd',
        sql=sql
        )

    context_ref = {
        'referencia': referencia,
        'headers': grade.table_data['header'],
        'fields': grade.table_data['fields'],
        'data': grade.table_data['data'],
        'total': grade.total,
    }

    return context_ref
