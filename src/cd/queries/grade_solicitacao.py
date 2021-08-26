from pprint import pprint

from utils.functions.models import GradeQtd

from cd.queries.functions import where_ende_disponivel


def grade_solicitacao(
        cursor, referencia=None, solicit_id=None, tipo='1s',
        grade_inventario=False):
    """
    referencia: None = grade total (da solicitação)
                string = filtra uma referência
                list = lista de referências
    tipo: 1s = uma solicitação
               solicit_id é obrigatório
          s = todas as solicitação
          p = todos os pedidos
          sp = todas as solicitação + todos os pedidos
          i = inventário
          i-s = disponível (inventário - todas as solicitações)
          i-sp = disponível (inventário - todas as solicitações - pedidos)
    grade_inventario: pega cores e tamanhos do inventário,
                      mesmo que o tipo seja outro
    referencia: pode ser uma referência oi uma lista de referências
    """

    filter_local = """--
        and l.local is not null
        and l.local <> ''
    """

    filter_local += where_ende_disponivel("l.local")

    # Grade de solicitação
    grade = GradeQtd(cursor)
    if tipo == '1s':
        grade_complementar = GradeQtd(cursor)

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

    # tamanhos
    if not grade_inventario and tipo == '1s':
        sql = f'''
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
        '''
    elif not grade_inventario and tipo == 's':
        sql = f'''
            SELECT
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
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
        '''
    elif not grade_inventario and tipo == 'p':
        sql = f'''
            SELECT distinct
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
              and o.pedido <> 0
            order by
              l.ordem_tamanho
        '''
    elif grade_inventario or tipo == 'i':
        sql = f'''
            SELECT distinct
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
              and l.qtd > 0
            order by
              l.ordem_tamanho
        '''
    elif not grade_inventario and tipo == 'i-s':
        sql = f'''
            SELECT
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
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
        '''
    elif not grade_inventario and tipo == 'i-sp':
        sql = f'''
            SELECT
              l.tamanho
            , l.ordem_tamanho
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
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
        '''
    grade.col(
        id='tamanho',
        name='Tamanho',
        total='Total',
        sql=sql
        )
    if tipo == '1s':
        grade_complementar.col(
            id='tamanho',
            name='Tamanho',
            total='Total',
            sql=sql
            )

    # cores
    if not grade_inventario and tipo == '1s':
        sql = f'''
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
        '''
    elif not grade_inventario and tipo == 's':
        sql = f'''
            SELECT
              l.cor
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
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
        '''
    elif not grade_inventario and tipo == 'p':
        sql = f'''
            SELECT distinct
              l.cor
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
              and o.pedido <> 0
            order by
              l.cor
        '''
    elif grade_inventario or tipo == 'i':
        sql = f'''
            SELECT distinct
              l.cor
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
              and l.qtd > 0
            order by
              l.cor
        '''
    elif not grade_inventario and tipo == 'i-s':
        sql = f'''
            SELECT
              l.cor
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
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
        '''
    elif not grade_inventario and tipo == 'i-sp':
        sql = f'''
            SELECT
              l.cor
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
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
        '''
    grade.row(
        id='cor',
        name='Cor',
        name_plural='Cores',
        total='Total',
        sql=sql
        )
    if tipo == '1s':
        grade_complementar.row(
            id='cor',
            name='Cor',
            name_plural='Cores',
            total='Total',
            sql=sql
            )

    # sortimento
    if tipo == '1s':
        sql = f'''
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
              {filter_local} -- filter_local
              {filter_solicit_id} -- filter_solicit_id
            group by
              l.tamanho
            , l.cor
            order by
              l.tamanho
            , l.cor
        '''
        sql_complementar = f'''
            SELECT
              l.tamanho
            , l.cor
            , sum(case when l.qtd < coalesce(sq.qtd, 0)
                  then coalesce(sq.qtd, 0) - l.qtd
                  else 0
                  end) qtd
            from fo2_cd_lote l
            join fo2_cd_solicita_lote_qtd sq
              on sq.lote_id = l.id
            where 1=1
              and sq.origin_id = 0
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
              {filter_solicit_id} -- filter_solicit_id
            group by
              l.tamanho
            , l.cor
            order by
              l.tamanho
            , l.cor
        '''
    elif tipo == 's':
        sql = f'''
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
              {filter_local} -- filter_local
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
        '''
    elif tipo == 'p':
        sql = f'''
            SELECT
              l.tamanho
            , l.cor
            , sum(l.qtd) qtd
            from fo2_cd_lote l
            join fo2_prod_op o
              on o.op = l.op
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
              and o.pedido <> 0
            group by
              l.tamanho
            , l.cor
            order by
              l.tamanho
            , l.cor
        '''
    elif tipo == 'sp':
        sql = f'''
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
              {filter_local} -- filter_local
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
        '''
    elif tipo == 'i':
        sql = f'''
            SELECT
              l.tamanho
            , l.cor
            , sum(l.qtd) qtd
            from fo2_cd_lote l
            where 1=1
              {filter_referencia} -- filter_referencia
              {filter_local} -- filter_local
            group by
              l.tamanho
            , l.cor
            order by
              l.tamanho
            , l.cor
        '''
    elif tipo == 'i-s':
        sql = f'''
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
              {filter_local} -- filter_local
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
        '''
    elif tipo == 'i-sp':
        sql = f'''
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
              {filter_local} -- filter_local
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
        '''
    grade.value(
        id='qtd',
        sql=sql
        )
    print(sql)

    if tipo == '1s':
        grade_complementar.value(
            id='qtd',
            sql=sql_complementar
            )
        data_complementar = grade_complementar.table_data['data']
        total_complementar = grade_complementar.total
    else:
        data_complementar = None
        total_complementar = 0

    fields = grade.table_data['fields']
    data = grade.table_data['data']
    style = grade.table_data['style']

    context_ref = {
        'referencia': referencia,
        'headers': grade.table_data['header'],
        'fields': fields,
        'data': data,
        'style': style,
        'total': grade.total,
        'data_complementar': data_complementar,
        'total_complementar': total_complementar,
    }

    return context_ref
