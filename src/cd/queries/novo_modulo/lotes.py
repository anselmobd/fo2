from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import only_digits


def sql_em_estoque(tipo=None, ref=None, get=None, colecao=None, sinal='+', field_list=None):
    """Monta SQL base de selecão de lotes
    - endereçados; e
    - no estágio 63
    Recebe:
      tipo
        i = inventário: todos os lotes endereçados e com quantidade no estágio 63
        p = lotes que aparece no inventário (opção acima) e são de OPs de Pedidos
        s = solicitado (situação 2, 3 ou 4) de OP com estágio 63
        iq = inventário: todos os lotes endereçados e com quantidade em qq estágio
        None = todos os lotes
      ref: filtro de referências
        None = não filtra
        {condição}string = uma referência
          condição: altera o funcionamento do filtro
            '' = igualdade
            '<' = menor que
            '>' = maior que
        list = uma lista de referências
      get
        ref = busca apenas o campo referência (com distinct)
        None = busca apenas o campo referência (sem distinct)
        lote_qtd = busca op, lote, item e quantidades
        # loc = busca op, lote, item, quantidades e informação de endereçamento
      sinal: positivo ou negativo
        '+' = quantidades como estão no banco de dados
        '-' = inverte o sinal das quantidades       
      #field_list
      #  Lista de fields que devem ser retornados
      #    Field pode ter alias a ser utilizado. Ex.: "qtd quanti"
      #    obs.: ref sempre é retornado
    """

    if ref is None:
        filter_ref = ''
    elif isinstance(ref, str):
        if ref[0] in ['<', '>']:
            condicao = ref[0]
            ref = ref[1:]
        else:
            condicao = '='
        filter_ref = f"and l.PROCONF_GRUPO {condicao} '{ref}'"
    else:
        refs = ', '.join([f"'{r}'" for r in ref])
        filter_ref = f"and l.PROCONF_GRUPO in ({refs})"

    join_para_colecao = ""
    filter_colecao = ""
    if colecao is not None:
        join_para_colecao = """
            JOIN BASI_030 r
              ON r.NIVEL_ESTRUTURA = 1
             AND r.REFERENCIA = l.PROCONF_GRUPO 
        """
        filter_colecao = f"AND r.COLECAO = '{colecao}'"

    field_list = field_list if field_list else []
    fields_set = {'ref'}.union(field_list)

    available_fields = {
        'ref': "l.PROCONF_GRUPO",
        'per': "l.PERIODO_PRODUCAO",
        'oc': "l.ORDEM_CONFECCAO",
        'tam': "l.PROCONF_SUBGRUPO",
        'ordem_tam': "tam.ORDEM_TAMANHO",
        'cor': "l.PROCONF_ITEM",
        'op': "l.ORDEM_PRODUCAO",
        'qtd_prog': "l.QTDE_PECAS_PROG",
        'qtd_dbaixa': "l.QTDE_DISPONIVEL_BAIXA",
    }

    distinct = False
    if get == 'ref':
        distinct = True
    elif get == 'lote_qtd':
        fields_set = fields_set.union([
            'per',
            'oc',
            'tam',
            'ordem_tam',
            'cor',
            'op',
            'qtd_prog',
            'qtd_dbaixa',
        ])

    filtra_estagio = "AND l.CODIGO_ESTAGIO = 63"
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
             AND sl.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000) 
        """
        tipo_filter = """--
              AND sl.SITUACAO IN (2, 3, 4)
        """
    elif tipo and tipo.startswith('i'):
        field_qtd = f"""--
            , {sinal}l.QTDE_DISPONIVEL_BAIXA qtd
        """
        tipo_join = ""
        tipo_filter = """--
              AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
        if 'q' in tipo:
            filtra_estagio = ''
    else:
        field_qtd = ""
        tipo_join = ""
        tipo_filter = """--
              AND l.QTDE_DISPONIVEL_BAIXA > 0
        """

    fields = "\n, ".join(
        [
            f"{available_fields[field.split()[0]]} {field.split()[-1]}"
            for field in fields_set
        ]
    )

    sql = f"""
        SELECT {"DISTINCT" if distinct else ""}
        {fields} -- fields
        {field_qtd} -- field_qtd
        FROM ENDR_014 lp
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO 
         AND l.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
        {tipo_join} -- tipo_join
        {join_para_colecao} -- join_para_colecao
        LEFT JOIN BASI_220 tam -- cadastro de tamanhos
          ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
          {filtra_estagio} -- filtra_estagio
          {tipo_filter} -- tipo_filter
          {filter_ref} -- filter_ref
          {filter_colecao} -- filter_colecao
    """
    return sql


def refs_em_estoque(cursor):
    sql = sql_em_estoque(get='ref')
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def lotes_em_estoque(cursor, tipo=None, ref=None, colecao=None, get=None, modelo=None, field_list=None):
    sql = sql_em_estoque(tipo=tipo, ref=ref, colecao=colecao, get=get, field_list=field_list)
    debug_cursor_execute(cursor, sql)
    dados = dictlist(cursor)
    if modelo:
        dados_modelo = []
    for row in dados:
        try:
            ref_modelo = int(only_digits(row['ref']))
        except ValueError:
            ref_modelo = 0
        row['modelo'] = ref_modelo
        if ref_modelo == modelo:
            dados_modelo.append(row)
    if modelo:
        return dados_modelo
    else:
        return dados
