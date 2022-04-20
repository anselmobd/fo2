from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


def sql_em_estoque(tipo=None, ref=None, get=None, sinal='+'):
    """Monta SQL base de selecão de lotes
    - endereçados; e
    - no estágio 63
    Recebe:
      tipo
        p = lotes de OPs de Pedidos
        s = solicitado (situação 2, 3 ou 4)
        i = inventário: todos os lotes com quantidade
        None = todos os lotes
      ref: filtro de referências
        None = não filtra
        string = uma referência
        list = uma lista de referências
      get
        ref = busca apenas o campo referência (com distinct)
        None = busca lote, item, op e quantidades
      sinal: positivo ou negativo
        '+' = quantidades como estão no banco de dados
        '-' = inverte o sinal das quantidades       
    """

    if ref is None:
        filter_ref = ''
    elif isinstance(ref, str):
        filter_ref = f"and l.PROCONF_GRUPO = '{ref}'"
    else:
        refs = ', '.join([f"'{r}'" for r in ref])
        filter_ref = f"and l.PROCONF_GRUPO in ({refs})"

    if get == 'ref':
        distinct = True
        fields = """--
              l.PROCONF_GRUPO ref
        """
    else:
        distinct = False
        fields = """--
              l.PERIODO_PRODUCAO per
            , l.ORDEM_CONFECCAO oc
            , l.PROCONF_GRUPO ref
            , l.PROCONF_SUBGRUPO tam
            , tam.ORDEM_TAMANHO ordem_tam
            , l.PROCONF_ITEM cor
            , l.ORDEM_PRODUCAO op
            , l.QTDE_PECAS_PROG qtd_prog
            , l.QTDE_DISPONIVEL_BAIXA qtd_dbaixa
        """

    if tipo == 'p':
        field_qtd = f"""--
            , {sinal}l.QTDE_DISPONIVEL_BAIXA qtd
        """
        tipo_join = """--
            JOIN PCPC_020 op
              ON op.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO
        """
        tipo_filter = """--
              AND op.PEDIDO_VENDA <> 0
              AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    elif tipo == 's':
        field_qtd = f"""--
            , {sinal}sl.QTDE qtd
        """
        tipo_join = """--
            JOIN PCPC_044 sl
              ON sl.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO
             AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO 
        """
        tipo_filter = """--
              AND sl.SITUACAO IN (2, 3, 4)
        """
    elif tipo == 'i':
        field_qtd = f"""--
            , {sinal}l.QTDE_DISPONIVEL_BAIXA qtd
        """
        tipo_join = ""
        tipo_filter = """--
              AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    else:
        field_qtd = ""
        tipo_join = ""
        tipo_filter = ""

    sql = f"""
        SELECT {"DISTINCT" if distinct else ""}
        {fields} -- fields
        {field_qtd} -- field_qtd
        FROM ENDR_014 lp
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO 
         AND l.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
        {tipo_join} -- tipo_join
        LEFT JOIN BASI_220 tam -- cadastro de tamanhos
          ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE l.CODIGO_ESTAGIO = 63
          {tipo_filter} -- tipo_filter
          {filter_ref} -- filter_ref
    """
    return sql


def refs_em_estoque(cursor):
    sql = sql_em_estoque(get='ref')
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def lotes_em_estoque(cursor, tipo=None, ref=None, get=None):
    sql = sql_em_estoque(tipo=tipo, ref=ref, get=get)
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
