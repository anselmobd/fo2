from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['op_producao']


def op_producao(
    cursor,
    modelo=None,
    tipo_ref=None,
    tipo_op=None,
    tipo_selecao=None,
):
    """
    tipo_ref:>None - Todas
              a - PA
              g - PG
              b - PB
              p - PG ou PB
              v - PA, PG ou PB
              m - MD
              i - MP
    tipo_op:>None - Todas
             e - OP de expedição (não tem estágio 63)
             p - OP de produção (tem estágio 63)
    tipo_selecao:>t - Todos os lotes
                  #a - Ainda não produzido / não finalizado
                  #fpnf - finalizado, de pedido, não faturado
                  #apf - a produzir, de pedido faturado
                  #p - Perda
                  #c - Conserto
                  #s - Segunda qualidade
                  #acd - estocada; "a", no CD (estágios 57 e 63)
                  ap - em produção; "a", não no CD (estágios não 57, 63 e 64)
    """

    join_tables = set()
    join_dict = {
        'BASI_030': """--
            JOIN BASI_030 r
              ON r.REFERENCIA = o.REFERENCIA_PECA
             AND r.NIVEL_ESTRUTURA = 1
        """
    }

    filtra_modelo = f"""--
         AND r.REFERENCIA LIKE '%2%'
         AND REGEXP_REPLACE(
               r.REFERENCIA
             , '^[a-zA-Z]?0*([123456789][0123456789]*)[a-zA-Z]*$'
             , '\\1'
             ) = '2'
    """ if modelo else ''

    if tipo_ref is None:
        filtro_tipo_ref = ''
    elif tipo_ref == 'a':
        filtro_tipo_ref = """--
            AND r.REFERENCIA < 'A0000'
        """
    elif tipo_ref == 'g':
        filtro_tipo_ref = """--
            AND r.REFERENCIA >= 'A0000'
            AND r.REFERENCIA < 'B0000'
        """
    elif tipo_ref == 'b':
        filtro_tipo_ref = """--
            AND r.REFERENCIA >= 'B0000'
            AND r.REFERENCIA < 'C0000'
        """
    elif tipo_ref == 'p':
        filtro_tipo_ref = """--
            AND r.REFERENCIA >= 'A0000'
            AND r.REFERENCIA < 'C0000'
        """
    elif tipo_ref == 'v':
        filtro_tipo_ref = """--
            AND r.REFERENCIA < 'C0000'
        """
    elif tipo_ref == 'm':
        filtro_tipo_ref = """--
            AND r.REFERENCIA >= 'C0000'
            AND r.REFERENCIA NOT LIKE 'F%'
        """
    elif tipo_ref == 'i':
        filtro_tipo_ref = """--
            AND r.REFERENCIA >= 'F0000'
            AND r.REFERENCIA < 'G0000'
        """

    if tipo_op is None:
        filtro_tipo_op = ''
    else:
        sql_not = "NOT" if tipo_op == 'e' else ''
        filtro_tipo_op = f"""--
            AND {sql_not} EXISTS (
              SELECT
                lto.CODIGO_ESTAGIO
              FROM PCPC_040 lto
              WHERE lto.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND lto.CODIGO_ESTAGIO = 63
            )
        """

    if filtra_modelo or filtro_tipo_ref:
        join_tables.add('BASI_030')

    join_stm = "\n".join([
        join_dict[t]
        for t in join_dict
        if t in join_tables
    ]) if join_tables else ''

    if tipo_selecao is None:  # todos
        filtro_tipo_selecao = ''
    elif tipo_selecao == 'ap':  # em produção; "a", não no CD (estágios não 57, 63 e 64)
        filtro_tipo_selecao = """--
            AND l.QTDE_DISPONIVEL_BAIXA > 0
            AND l.CODIGO_ESTAGIO NOT IN (57, 63) --, 64)
        """


    sql = f"""
        SELECT
          l.PROCONF_ITEM COR
        , l.PROCONF_SUBGRUPO TAM
        , tam.ORDEM_TAMANHO ORDEM_TAM
        , SUM( l.QTDE_DISPONIVEL_BAIXA ) QTD
        FROM pcpc_020 o
        {join_stm} -- join_stm
        {filtra_modelo} -- filtra_modelo
        {filtro_tipo_ref} -- filtro_tipo_ref
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
          -- OP não cancelada
          AND o.SITUACAO <> 9
          AND o.COD_CANCELAMENTO = 0
          AND o.DT_CANCELAMENTO IS NULL
          {filtro_tipo_op} -- filtro_tipo_op
          {filtro_tipo_selecao} -- filtro_tipo_selecao
        GROUP BY
          tam.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
        ORDER BY
          tam.ORDEM_TAMANHO
        , l.PROCONF_ITEM
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    return dados
