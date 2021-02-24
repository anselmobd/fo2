from utils.functions.models import rows_to_dict_list


def op_relacionamentos(cursor, op, ref=None):
    if ref is None:
        ref = ''
    sql = f'''
        WITH ordemp AS
        (
          SELECT
            o.ORDEM_PRODUCAO
          , o.ORDEM_PRINCIPAL
          , o.ORDEM_MESTRE
          , o.COD_CANCELAMENTO
          FROM PCPC_020 o
          WHERE o.ORDEM_PRODUCAO  = {op}
        )
        SELECT
          o.ORDEM_PRODUCAO OP
        , 1
        , CAST('é Mãe de' AS varchar2(50)) REL
        , coalesce(ofi.ORDEM_PRODUCAO, 0) OP_REL
        , ofi.COD_CANCELAMENTO CANC
        FROM ordemp o
        JOIN PCPC_020 ofi
          ON ofi.ORDEM_PRINCIPAL = o.ORDEM_PRODUCAO
        where '{ref}' is null
           or ofi.REFERENCIA_PECA = '{ref}'
        --
        UNION
        --
        SELECT
          o.ORDEM_PRODUCAO OP
        , 2
        , CAST('é Avó de' AS varchar2(50)) REL
        , coalesce(one.ORDEM_PRODUCAO, 0) OP_REL
        , one.COD_CANCELAMENTO CANC
        FROM ordemp o
        JOIN PCPC_020 ofi
          ON ofi.ORDEM_PRINCIPAL = o.ORDEM_PRODUCAO
        JOIN PCPC_020 one
          ON one.ORDEM_PRINCIPAL = ofi.ORDEM_PRODUCAO
        where '{ref}' is null
           or one.REFERENCIA_PECA = '{ref}'
        --
        UNION
        --
        SELECT
          o.ORDEM_PRODUCAO OP
        , 3
        , CAST('é Filha de' AS varchar2(50)) REL
        , omae.ORDEM_PRODUCAO OP_REL
        , omae.COD_CANCELAMENTO CANC
        FROM ordemp o
        JOIN PCPC_020 omae
          ON omae.ORDEM_PRODUCAO = o.ORDEM_PRINCIPAL
        WHERE o.ORDEM_PRINCIPAL <> 0
          and ( '{ref}' is null
                or omae.REFERENCIA_PECA = '{ref}'
              )
        --
        UNION
        --
        SELECT
          o.ORDEM_PRODUCAO OP
        , 4
        , CAST('é Neta de' AS varchar2(50)) REL
        , oavo.ORDEM_PRODUCAO OP_REL
        , oavo.COD_CANCELAMENTO CANC
        FROM ordemp o
        JOIN PCPC_020 omae
          ON omae.ORDEM_PRODUCAO = o.ORDEM_PRINCIPAL
        JOIN PCPC_020 oavo
          ON oavo.ORDEM_PRODUCAO = omae.ORDEM_PRINCIPAL
        WHERE o.ORDEM_PRINCIPAL <> 0
          AND omae.ORDEM_PRINCIPAL <> 0
          and ( '{ref}' is null
                or oavo.REFERENCIA_PECA = '{ref}'
              )
        --
        UNION
        --
        SELECT
          o.ORDEM_PRODUCAO OP
        , 5
        , CAST('é Mestra de' AS varchar2(50)) REL
        , ose.ORDEM_PRODUCAO OP_REL
        , ose.COD_CANCELAMENTO CANC
        FROM ordemp o
        JOIN PCPC_020 ose
          ON ose.ORDEM_MESTRE = o.ORDEM_PRODUCAO
        where ( '{ref}' is null
                or ose.REFERENCIA_PECA = '{ref}'
              )
        --
        UNION
        --
        SELECT
          o.ORDEM_PRODUCAO OP
        , 6
        , CAST('é Seguidora de' AS varchar2(50)) REL
        , ome.ORDEM_PRODUCAO OP_REL
        , ome.COD_CANCELAMENTO CANC
        FROM ordemp o
        JOIN PCPC_020 ome
          ON ome.ORDEM_PRODUCAO = o.ORDEM_MESTRE
        WHERE o.ORDEM_MESTRE <> 0
          and ( '{ref}' is null
                or ome.REFERENCIA_PECA = '{ref}'
              )
        --
        ORDER BY
          2
        , 1
    '''
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
