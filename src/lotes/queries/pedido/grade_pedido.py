from pprint import pprint

from utils.functions import arg_def
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import modelo_de_ref

__all__ = ['query']


def query(
    cursor,
    agrupamento='ct',
    empresa=1,
    pedido=None,
    ref=None,
    modelo=None,
    periodo=None,
    cancelado='t',
    liberado='t',
    faturado='t',
    faturavel='t',
    solicitado='t',
    agrupado_em_solicitacao='t',
):
    """Return total de quantidade pedida por
    agrupamento (referência e/ou cor e/ou tamanho)
    Filtra por:
        agrupamento - default 'ct' (cor, tamanho)
            totaliza por quais campos
            'rct' (ref., cor, tamanho)
        empresa - default 1 (matriz)
        pedido - default não filtra
            um número de pedido específico
        ref - default não filtra
            referência, que pode ser unica (string)
            ou tupla ou lista de referências
        modelo - default não filtra
            um modelo específico
        periodo - default não filtra
            período de data de embarque do pedido
            string com ':' separando dois números (opcionais)
            significando quantidade de dias após o dia corrente.
            o primeiro referente à data inicial (não inclusa) e
            o segundo referente à data final (inclusa) do período.
        cancelado - default 't' todos os pedidos
            'c' ou 'i' - cancelado ou inativo
            'n' ou 'a' - não cancelado ou ativo
        liberado - default 't' todos os pedidos
            pedido liberado (SITUACAO_VENDA = 0)
            's' - liberado
            'n' - não liberado
        faturado - default 't' todos os pedidos
            'f' - faturado (obs.: não verifica se foi devolvido)
            'n' - não faturado
        faturavel - default 't' todos os pedidos
            'f' - faturavel (não faturado)
            'n' - não faturavel (faturado - obs.: não verifica se foi devolvido)
        solicitado - default 't' todos os pedidos
            existe solicitação do com pedido destino igual ao pedido em 
            questão e esta solicitação está com situação diferente de zero
            's' - solicitado
            'n' - não solicitado
        agrupado_em_solicitacao - default 't' todos os pedidos
            pedido agrupado em empenho para varejo
            's' - agrupado
            'n' - não agrupado
    """

    filtro_empresa = f"""--
        AND ped.CODIGO_EMPRESA = {empresa}
    """

    filtra_pedido = f"AND i.PEDIDO_VENDA = {pedido}" if pedido else ''

    if ref:
        if isinstance(ref, (tuple, list)):
            refs = set(ref)
        else:
            refs = {ref, }
        refs_sql = ', '.join(list(refs))
        filtra_ref = f"""--
            AND r.REFERENCIA in ({refs_sql})
        """
    else:
        filtra_ref = ''

    filtra_modelo = f"""--
         AND r.REFERENCIA LIKE '%{modelo}%'
         AND REGEXP_REPLACE(
               r.REFERENCIA
             , '^[a-zA-Z]?0*([123456789][0123456789]*)[a-zA-Z]*$'
             , '\\1'
             ) = '{modelo}'
    """ if modelo else ''

    filtra_periodo = ''
    if periodo and ':' in periodo:
        periodo_list = periodo.split(':')
        if periodo_list[0] != '':
            filtra_periodo += f"""--
                AND ped.DATA_ENTR_VENDA > CURRENT_DATE + {periodo_list[0]}
            """
        if periodo_list[1] != '':
            filtra_periodo += f"""--
                AND ped.DATA_ENTR_VENDA <= CURRENT_DATE + {periodo_list[1]}
            """

    if cancelado in ['c', 'i']:
        filtro_cancelado = """--
            AND ped.STATUS_PEDIDO = 5
        """
    elif cancelado in ['n', 'a']:
        filtro_cancelado = """--
            AND ped.STATUS_PEDIDO <> 5
        """
    else:
        filtro_cancelado = ''

    if liberado == 's':
        filtro_liberado = """--
            AND ped.SITUACAO_VENDA = 0
        """
    elif liberado == 'n':
        filtro_liberado = """--
            AND ped.SITUACAO_VENDA <> 0
        """
    else:
        filtro_liberado = ''

    if faturado == 't':
        filtro_faturado = ''
    else:
        exists = 'NOT' if faturado == 'f' else ''
        filtro_faturado = f"""--
            AND f.NUM_NOTA_FISCAL IS {exists} NULL
        """

    if faturavel == 't':
        filtro_faturavel = ''
    else:
        exists = 'NOT' if faturavel == 'n' else ''
        filtro_faturavel = f"""--
            AND fok.NUM_NOTA_FISCAL IS {exists} NULL
        """

    if solicitado == 't':
        filtro_solicitado = ''
    else:
        exists = 'NOT' if solicitado == 'n' else ''
        filtro_solicitado = f"""--
            AND {exists} EXISTS
                ( SELECT
                    1
                  FROM pcpc_044 sl -- solicitação / lote 
                  WHERE sl.PEDIDO_DESTINO = i.PEDIDO_VENDA
                    AND sl.SITUACAO <> 0
                )
        """

    if agrupado_em_solicitacao == 't':
        filtro_agrupado_em_solicitacao = ''
    else:
        exists = 'NOT' if agrupado_em_solicitacao == 'n' else ''
        filtro_agrupado_em_solicitacao = f"""--
            AND {exists} EXISTS
                ( SELECT
                    1
                  FROM PEDI_110 iped -- item de pedido de venda
                  WHERE iped.PEDIDO_VENDA = i.PEDIDO_VENDA
                    AND iped.AGRUPADOR_PRODUCAO <> 0
                )
        """

    sql_agrupamento = {
        'rct': {
            'select': """--
                  i.CD_IT_PE_GRUPO REF
                , i.CD_IT_PE_ITEM COR
                , i.CD_IT_PE_SUBGRUPO TAM
                , t.ORDEM_TAMANHO ORDEM_TAM
            """,
            'group_order': """--
                  i.CD_IT_PE_GRUPO
                , i.CD_IT_PE_ITEM
                , t.ORDEM_TAMANHO
                , i.CD_IT_PE_SUBGRUPO
            """,
        },
        'ct': {
            'select': """--
                  i.CD_IT_PE_ITEM COR
                , i.CD_IT_PE_SUBGRUPO TAM
                , t.ORDEM_TAMANHO ORDEM_TAM
            """,
            'group_order': """--
                  i.CD_IT_PE_ITEM
                , t.ORDEM_TAMANHO
                , i.CD_IT_PE_SUBGRUPO
            """,
        },
    }

    sql=f"""
        SELECT
          {sql_agrupamento[agrupamento]['select']}
        , sum(i.QTDE_PEDIDA) QUANTIDADE
        FROM PEDI_110 i -- item de pedido de venda
        JOIN BASI_030 r
          ON r.REFERENCIA = i.CD_IT_PE_GRUPO
         AND r.NIVEL_ESTRUTURA = 1
        JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = i.PEDIDO_VENDA
        LEFT JOIN FATU_050 f -- fatura
          ON f.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND f.SITUACAO_NFISC <> 2  -- cancelada
         AND f.NUMERO_CAIXA_ECF = 0
        LEFT JOIN FATU_050 fok -- fatura
          ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND fok.SITUACAO_NFISC <> 2  -- cancelada
         AND fok.NUMERO_CAIXA_ECF = 0
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = i.CD_IT_PE_SUBGRUPO
        LEFT JOIN BASI_010 rtc -- item (ref+tam+cor)
          on rtc.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99
         AND rtc.GRUPO_ESTRUTURA = i.CD_IT_PE_GRUPO
         AND rtc.SUBGRU_ESTRUTURA = i.CD_IT_PE_SUBGRUPO
         AND rtc.ITEM_ESTRUTURA = i.CD_IT_PE_ITEM
        WHERE 1=1
          {filtro_empresa} -- filtro_empresa
          {filtra_pedido} -- filtra_pedido
          {filtra_ref} -- filtra_ref
          {filtra_modelo} -- filtra_modelo
          {filtra_periodo} -- filtra_periodo
          {filtro_cancelado} -- filtro_cancelado
          {filtro_liberado} -- filtro_liberado
          {filtro_faturado} -- filtro_faturado
          {filtro_faturavel} -- filtro_faturavel
          {filtro_solicitado} -- filtro_solicitado
          {filtro_agrupado_em_solicitacao} -- filtro_agrupado_em_solicitacao
        GROUP BY
          {sql_agrupamento[agrupamento]['group_order']}
        ORDER BY
          {sql_agrupamento[agrupamento]['group_order']}
    """

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    if dados and 'ref' in dados[0]:
        for row in dados:
            row['modelo'] = modelo_de_ref(row['ref'])

    return dados
