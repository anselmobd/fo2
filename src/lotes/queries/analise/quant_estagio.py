from pprint import pprint

from utils.functions.models import rows_to_dict_list
from utils.functions.queries import coalesce, sql_where, sql_where_none_if


def quant_estagio(
        cursor, estagio=None, ref=None, tipo=None, cor=None, tam=None,
        only=None, less=None, group=None, deposito=None):

    filtra_estagios = ' '.join([
        sql_where('l.CODIGO_ESTAGIO', only, operation="IN"),
        sql_where('l.CODIGO_ESTAGIO', less, operation="NOT IN"),
    ])

    filtra_estagio = sql_where_none_if('l.CODIGO_ESTAGIO', estagio, '')

    ref = coalesce(ref, '')
    filtra_ref = sql_where_none_if(
        'l.PROCONF_GRUPO', ref, '',
        operation="LIKE" if '%' in ref else "=")

    filtro_tam = sql_where_none_if('l.PROCONF_SUBGRUPO', tam, '')

    filtro_cor = sql_where_none_if('l.PROCONF_ITEM', cor, '')

    filtro_deposito = sql_where('o.DEPOSITO_ENTRADA', deposito, quote='')

    group_params = {
        'o': ['o.ORDEM_PRODUCAO'],
        'op': ['o.ORDEM_PRODUCAO', 'o.PEDIDO_VENDA'],
    }
    print(group)
    filtro_group = ''
    if group in group_params:
        filtro_group = ', '.join([""]+group_params[group])

    OPERATION_IDX = 0
    VALUE_IDX = 1
    tipo_params = {
        'a': ["<", "A0000"],
        'g': ["LIKE", "A%"],
        'b': ["LIKE", "B%"],
        'p': ["LIKE", ("A%", "B%")],
        'v': ["<", "C0000"],
        'm': [">=", "C0000"],
    }
    filtro_tipo = ""
    if tipo in tipo_params:
        filtro_tipo = sql_where(
            'l.PROCONF_GRUPO',
            tipo_params[tipo][VALUE_IDX],
            operation=tipo_params[tipo][OPERATION_IDX],
        )

    sql = f"""
        SELECT
          sum(
            CASE WHEN (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
            THEN 1
            ELSE 0
            END
          ) LOTES
        , sum((l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)) QUANT
        {filtro_group} -- filtro_group
        , l.PROCONF_NIVEL99 NIVEL
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        FROM PCPC_040 l
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
          AND o.SITUACAO in (4, 2) -- Ordens em produção, Ordem confec. gerada
          {filtro_deposito} -- filtro_deposito
        --  AND l.PERIODO_PRODUCAO = 1921
        --  AND l.ORDEM_CONFECCAO = 01866
          {filtra_estagio} -- filtra_estagio
          {filtra_estagios} -- filtra_estagios
          {filtra_ref} -- filtra_ref
          {filtro_tipo} -- filtro_tipo
          {filtro_tam} -- filtro_tam
          {filtro_cor} -- filtro_cor
        GROUP BY
          l.PROCONF_NIVEL99
        {filtro_group} -- filtro_group
        , l.PROCONF_GRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
        HAVING
          sum((l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)) > 0
        ORDER BY
          l.PROCONF_NIVEL99
        {filtro_group} -- filtro_group
        , l.PROCONF_GRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_ITEM
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
