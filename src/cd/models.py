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


# tipo: s = solicitação
#           se solicit_id, então: uma solicitação
#                          senão: todas as solicitação
#       i = inventário
#       d = disponível (inventário - todas as solicitações)
def grade_solicitacao(cursor, referencia, solicit_id=None, tipo='s'):
    # Grade de solicitação
    grade = GradeQtd(cursor, [referencia])

    if solicit_id is None:
        filter_solicit_id = '''
            and case when l.qtd < sq.qtd
              then l.qtd
              else sq.qtd
              end > 0
        '''
    else:
        filter_solicit_id = 'and sq.solicitacao_id = {}'.format(solicit_id)

    # tamanhos
    if tipo == 's':
        sql = '''
            SELECT distinct
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            join fo2_cd_solicita_lote_qtd sq
              on sq.lote_id = l.id
            where l.referencia = %s
              {filter_solicit_id}
            order by
              l.ordem_tamanho
        '''.format(
            filter_solicit_id=filter_solicit_id)
    elif tipo == 'i':
        sql = '''
            SELECT distinct
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            where l.referencia = %s
              and l.qtd > 0
            order by
              l.ordem_tamanho
        '''
    elif tipo == 'd':
        sql = '''
            SELECT distinct
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            left join fo2_cd_solicita_lote_qtd sq
              on sq.lote_id = l.id
            where l.referencia = %s
            group by
              l.ordem_tamanho
            , l.tamanho
            having
              sum(l.qtd) - sum(min(coalesce(sq.qtd, 0), l.qtd)) > 0
            order by
              l.ordem_tamanho
        '''
    grade.col(
        id='tamanho',
        name='Tamanho',
        total='Total',
        sql=sql
        )

    # cores
    if tipo == 's':
        sql = '''
            SELECT distinct
              l.cor
            from fo2_cd_lote l
            join fo2_cd_solicita_lote_qtd sq
              on sq.lote_id = l.id
            where l.referencia = %s
              {filter_solicit_id}
            order by
              l.cor
        '''.format(
            filter_solicit_id=filter_solicit_id)
    elif tipo == 'i':
        sql = '''
            SELECT distinct
              l.cor
            from fo2_cd_lote l
            where l.referencia = %s
              and l.qtd > 0
            order by
              l.cor
        '''
    elif tipo == 'd':
        sql = '''
            SELECT distinct
              l.cor
            from fo2_cd_lote l
            left join fo2_cd_solicita_lote_qtd sq
              on sq.lote_id = l.id
            where l.referencia = %s
            group by
              l.cor
            having
              sum(l.qtd) - sum(min(coalesce(sq.qtd, 0), l.qtd)) > 0
            order by
              l.cor
        '''
    grade.row(
        id='cor',
        name='Cor',
        name_plural='Cores',
        total='Total',
        sql=sql
        )

    # sortimento
    if tipo == 's':
        sql = '''
            SELECT distinct
              l.tamanho
            , l.cor
            , sum(sq.qtd) qtd
            from fo2_cd_lote l
            join fo2_cd_solicita_lote_qtd sq
              on sq.lote_id = l.id
            where l.referencia = %s
              {filter_solicit_id}
            group by
              l.tamanho
            , l.cor
            order by
              l.tamanho
            , l.cor
        '''.format(
            filter_solicit_id=filter_solicit_id)
    elif tipo == 'i':
        sql = '''
            SELECT distinct
              l.tamanho
            , l.cor
            , sum(l.qtd) qtd
            from fo2_cd_lote l
            where l.referencia = %s
            group by
              l.tamanho
            , l.cor
            order by
              l.tamanho
            , l.cor
        '''
    elif tipo == 'd':
        sql = '''
            SELECT distinct
              l.tamanho
            , l.cor
            , sum(l.qtd) - sum(min(coalesce(sq.qtd, 0), l.qtd)) qtd
            from fo2_cd_lote l
            left join fo2_cd_solicita_lote_qtd sq
              on sq.lote_id = l.id
            where l.referencia = %s
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
