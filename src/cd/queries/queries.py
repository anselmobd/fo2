from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower

import lotes.models


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
            -- , le.QTDE_EM_PRODUCAO_PACOTE QTD
            , le.QTDE_DISPONIVEL_BAIXA + le.QTDE_CONSERTO QTD
            FROM PCPC_040 le -- lote estágio atual
            --WHERE le.QTDE_EM_PRODUCAO_PACOTE <> 0
            WHERE 1=1
              AND le.QTDE_PECAS_PROG IS NOT NULL
              AND le.QTDE_PECAS_PROG <> 0
              AND (le.QTDE_DISPONIVEL_BAIXA + le.QTDE_CONSERTO) <> 0
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
            --WHERE le.QTDE_EM_PRODUCAO_PACOTE = 0
            WHERE le.QTDE_PECAS_PROG IS NOT NULL
              AND le.QTDE_PECAS_PROG <> 0
              AND le.QTDE_PECAS_PROD <> 0
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


def sum_pedido(cursor, referencia=None):

    end_disp = list(lotes.models.EnderecoDisponivel.objects.all().values())

    filter_local = """--
        and l.local is not null
        and l.local <> ''
    """
    if len(end_disp) != 0:
        filter_end = """--
            AND l.local ~ '^("""
        filter_sep = ""
        for regra in end_disp:
            filter_end += f"{filter_sep}{regra['inicio']}"
            filter_sep = "|"
        filter_local += filter_end + """).*'
        """

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
          {filter_local} -- filter_local
          and o.pedido <> 0
    '''.format(
        filter_referencia=filter_referencia,
        filter_local=filter_local,
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
        , l.estagio 
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
