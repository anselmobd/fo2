from pprint import pprint

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


# referencia: None = grade total (da solicitação)
#             string = filtra uma referência
#             list = lista de referências
# tipo: 1s = uma solicitação
#            solicit_id é obrigatório
#       s = todas as solicitação
#       p = todos os pedidos
#       sp = todas as solicitação + todos os pedidos
#       i = inventário
#       i-s = disponível (inventário - todas as solicitações)
#       i-sp = disponível (inventário - todas as solicitações - pedidos)
# grade_inventario: pega cores e tamanhos do inventário,
#                   mesmo que o tipo seja outro
# referencia: pode ser uma referência oi uma lista de referências
def grade_solicitacao(
        cursor, referencia=None, solicit_id=None, tipo='1s',
        grade_inventario=False):

    # Grade de solicitação
    grade = GradeQtd(cursor)

    if referencia is None:
        filter_referencia = '--'
    elif isinstance(referencia, str):
        filter_referencia = "and l.referencia = '{}'".format(referencia)
    else:
        filter_referencia = "and l.referencia in ("
        sep = ''
        for ref in referencia:
            filter_referencia += "{}'{}'".format(sep, ref)
            sep = ', '
        filter_referencia += ")"

    if solicit_id is None:
        filter_solicit_id = ''
    else:
        filter_solicit_id = 'and sq.solicitacao_id = {}'.format(solicit_id)

    filtros = {
        'filter_solicit_id': filter_solicit_id,
        'filter_referencia': filter_referencia,
    }

    # tamanhos
    if not grade_inventario and tipo == '1s':
        sql = '''
            SELECT distinct
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            join fo2_cd_solicita_lote_qtd sq
              on sq.lote_id = l.id
            where 1=1
              and sq.origin_id = 0
              {filter_referencia} -- filter_referencia
              {filter_solicit_id} -- filter_solicit_id
            order by
              l.ordem_tamanho
        '''.format(**filtros)
    elif not grade_inventario and tipo == 's':
        sql = '''
            SELECT
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
            group by
              l.tamanho
            , l.ordem_tamanho
            having
              sum(
                case
                when l.qtd < coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                then l.qtd
                else coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                end
              ) > 0
            order by
              l.ordem_tamanho
        '''.format(**filtros)
    elif not grade_inventario and tipo == 'p':
        sql = '''
            SELECT distinct
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
              and o.pedido <> 0
            order by
              l.ordem_tamanho
        '''.format(**filtros)
    elif grade_inventario or tipo == 'i':
        sql = '''
            SELECT distinct
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
              and l.qtd > 0
            order by
              l.ordem_tamanho
        '''.format(**filtros)
    elif not grade_inventario and tipo == 'i-s':
        sql = '''
            SELECT
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
            group by
              l.tamanho
            , l.ordem_tamanho
            having
              sum( l.qtd -
                case
                when l.qtd < coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                then l.qtd
                else coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                end
              ) > 0
            order by
              l.ordem_tamanho
        '''.format(**filtros)
    elif not grade_inventario and tipo == 'i-sp':
        sql = '''
            SELECT
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
            group by
              l.tamanho
            , l.ordem_tamanho
            having
              sum(
                l.qtd
              - case when o.pedido <> 0 then l.qtd
                else
                  case
                  when l.qtd < coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  then l.qtd
                  else coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  end
                end
              ) > 0
            order by
              l.ordem_tamanho
        '''.format(**filtros)
    grade.col(
        id='tamanho',
        name='Tamanho',
        total='Total',
        sql=sql
        )

    # cores
    if not grade_inventario and tipo == '1s':
        sql = '''
            SELECT distinct
              l.cor
            from fo2_cd_lote l
            join fo2_cd_solicita_lote_qtd sq
              on sq.lote_id = l.id
            where 1=1
              and sq.origin_id = 0
              {filter_referencia} -- filter_referencia
              {filter_solicit_id} -- filter_solicit_id
            order by
              l.cor
        '''.format(**filtros)
    elif not grade_inventario and tipo == 's':
        sql = '''
            SELECT
              l.cor
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
            group by
              l.cor
            having
              sum(
                case
                when l.qtd < coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                then l.qtd
                else coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                end
              ) > 0
            order by
              l.cor
        '''.format(**filtros)
    elif not grade_inventario and tipo == 'p':
        sql = '''
            SELECT distinct
              l.cor
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
              and o.pedido <> 0
            order by
              l.cor
        '''.format(**filtros)
    elif grade_inventario or tipo == 'i':
        sql = '''
            SELECT distinct
              l.cor
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
              and l.qtd > 0
            order by
              l.cor
        '''.format(**filtros)
    elif not grade_inventario and tipo == 'i-s':
        sql = '''
            SELECT
              l.cor
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
            group by
              l.cor
            having
              sum( l.qtd -
                case
                when l.qtd < coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                then l.qtd
                else coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                end
              ) > 0
            order by
              l.cor
        '''.format(**filtros)
    elif not grade_inventario and tipo == 'i-sp':
        sql = '''
            SELECT
              l.cor
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
            group by
              l.cor
            having
              sum(
                l.qtd
              - case when o.pedido <> 0 then l.qtd
                else
                  case
                  when l.qtd < coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  then l.qtd
                  else coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  end
                end
              ) > 0
            order by
              l.cor
        '''.format(**filtros)
    grade.row(
        id='cor',
        name='Cor',
        name_plural='Cores',
        total='Total',
        sql=sql
        )

    # sortimento
    if tipo == '1s':
        sql = '''
            SELECT
              l.tamanho
            , l.cor
            , sum(case when l.qtd < coalesce(sq.qtd, 0)
                  then l.qtd
                  else coalesce(sq.qtd, 0)
                  end) qtd
            from fo2_cd_lote l
            join fo2_cd_solicita_lote_qtd sq
              on sq.lote_id = l.id
            where 1=1
              and sq.origin_id = 0
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
              {filter_solicit_id} -- filter_solicit_id
            group by
              l.tamanho
            , l.cor
            order by
              l.tamanho
            , l.cor
        '''.format(**filtros)
    elif tipo == 's':
        sql = '''
            SELECT
              l.tamanho
            , l.cor
            , sum(
                case
                when l.qtd < coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                then l.qtd
                else coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                end
              ) qtd
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
            group by
              l.tamanho
            , l.cor
            having
              sum(
                case
                when l.qtd < coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                then l.qtd
                else coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                end
              ) > 0
            order by
              l.tamanho
            , l.cor
        '''.format(**filtros)
    elif tipo == 'p':
        sql = '''
            SELECT
              l.tamanho
            , l.cor
            , sum(l.qtd) qtd
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
              and o.pedido <> 0
            group by
              l.tamanho
            , l.cor
            order by
              l.tamanho
            , l.cor
        '''.format(**filtros)
    elif tipo == 'sp':
        sql = '''
            SELECT
              l.tamanho
            , l.cor
            , sum(
                case when o.pedido <> 0 then l.qtd
                else
                  case
                  when l.qtd < coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  then l.qtd
                  else coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  end
                end
              ) qtd
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
              and ( o.pedido <> 0
                  or coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0) > 0
                  )
            group by
              l.tamanho
            , l.cor
            having
              sum(
                case when o.pedido <> 0 then l.qtd
                else
                  case
                  when l.qtd < coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  then l.qtd
                  else coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  end
                end
              ) > 0
            order by
              l.tamanho
            , l.cor
        '''.format(**filtros)
    elif tipo == 'i':
        sql = '''
            SELECT
              l.tamanho
            , l.cor
            , sum(l.qtd) qtd
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
            group by
              l.tamanho
            , l.cor
            order by
              l.tamanho
            , l.cor
        '''.format(**filtros)
    elif tipo == 'i-s':
        sql = '''
            SELECT
              l.tamanho
            , l.cor
            , sum( l.qtd -
                case
                when l.qtd < coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                then l.qtd
                else coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                end
              ) qtd
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
            group by
              l.tamanho
            , l.cor
            having
              sum( l.qtd -
                case
                when l.qtd < coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                then l.qtd
                else coalesce(
                  ( select
                      sum(ss.qtd) qtd
                    from fo2_cd_solicita_lote_qtd ss
                    where ss.lote_id = l.id
                      and ss.origin_id = 0
                  ), 0)
                end
              ) > 0
            order by
              l.tamanho
            , l.cor
        '''.format(**filtros)
    elif tipo == 'i-sp':
        sql = '''
            SELECT
              l.tamanho
            , l.cor
            , sum(
                l.qtd
              - case when o.pedido <> 0 then l.qtd
                else
                  case
                  when l.qtd < coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  then l.qtd
                  else coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  end
                end
              ) qtd
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              and l.local is not null
              and l.local <> ''
            group by
              l.tamanho
            , l.cor
            having
              sum(
                l.qtd
              - case when o.pedido <> 0 then l.qtd
                else
                  case
                  when l.qtd < coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  then l.qtd
                  else coalesce(
                    ( select
                        sum(ss.qtd) qtd
                      from fo2_cd_solicita_lote_qtd ss
                      where ss.lote_id = l.id
                        and ss.origin_id = 0
                    ), 0)
                  end
                end
              ) > 0
            order by
              l.tamanho
            , l.cor
        '''.format(**filtros)
    grade.value(
        id='qtd',
        sql=sql
        )

    fields = grade.table_data['fields']
    data = grade.table_data['data']
    style = {}
    right_style = 'text-align: right;'
    bold_style = 'font-weight: bold;'
    for i in range(2, len(fields)):
        style[i] = right_style
    style[len(fields)] = right_style + bold_style
    data[-1]['|STYLE'] = bold_style

    context_ref = {
        'referencia': referencia,
        'headers': grade.table_data['header'],
        'fields': fields,
        'data': data,
        'style': style,
        'total': grade.total,
    }

    return context_ref


def sum_pedido(cursor, referencia=None):

    if referencia is None:
        filter_referencia = '--'
    elif isinstance(referencia, str):
        filter_referencia = "and l.referencia = '{}'".format(referencia)
    else:
        filter_referencia = "and l.referencia in ("
        sep = ''
        for ref in referencia:
            filter_referencia += "{}'{}'".format(sep, ref)
            sep = ', '
        filter_referencia += ")"

    sql = '''
        SELECT
          sum(l.qtd) qtd
        from fo2_cd_lote l
        join fo2_prod_op o
          on o.op = l.op
        where 1=1
          {filter_referencia} -- filter_referencia
          and l.local is not null
          and l.local <> ''
          and o.pedido <> 0
    '''.format(
        filter_referencia=filter_referencia,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def historico(cursor, op):
    sql = '''
        SELECT
          date(l.local_at) dt
        , count(*) qtd
        , l."local" endereco
        , u.username usuario
        from fo2_cd_lote l
        left join auth_user u
          on u.id = l.local_usuario_id
        where l.op = %s
        group by
          date(l.local_at)
        , l."local"
        , u.username
        order by
          1
        , l."local"
        , u.username
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list_lower(cursor)


def historico_detalhe(cursor, op):
    sql = '''
        SELECT
          date(l.local_at) dt
        , l.lote
        , l."local" endereco
        , u.username usuario
        from fo2_cd_lote l
        left join auth_user u
          on u.id = l.local_usuario_id
        where l.op = %s
        order by
          1
        , l."local"
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list_lower(cursor)


def historico_lote(cursor, lote):
    sql = '''
        select
          t.*
        from fo2_cd_lote l
        join fo2_ger_record_tracking t
          on t."table" = 'Lote'
         and t.record_id = l.id
        where l.lote = %s
          and t.iud = 'u'
        order by
          t."time"
    '''
    cursor.execute(sql, [lote])
    return rows_to_dict_list_lower(cursor)


def solicita_lote(cursor):
    sql = '''
        select
          s.id
        , s.codigo
        , s.descricao
        , s.ativa
        , s.create_at
        , s.update_at
        , s.usuario_id
        , u.username usuario__username
        , sum(sq.qtd) total_qtd
        , sum(
            case when l.local is null
            then 0
            else sq.qtd
            end
          ) total_no_cd
        from fo2_cd_solicita_lote s
        left join fo2_cd_solicita_lote_qtd sq
          on sq.solicitacao_id = s.id
         and sq.origin_id = 0
        left join fo2_cd_lote l
          on l.id = sq.lote_id
        left join auth_user u
          on u.id = s.usuario_id
        group by
          s.id
        , s.codigo
        , s.descricao
        , s.ativa
        , s.create_at
        , s.update_at
        , s.usuario_id
        , u.username
        order by
          s.update_at desc
    '''
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
