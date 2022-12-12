from pprint import pprint

from utils.functions import arg_def
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from cd.queries.novo_modulo.gerais import get_filtra_ref

__all__ = ['query']


def query(cursor, **kwargs):
    """Return total de quantidade pedida por referência/cor/tamanho
    Filtra por:
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
        agrupado - default 't' todos os pedidos
            agrupado em empenho para varejo
            's' - agrupado
            'n' - não agrupado
        pedido_liberado - default 't' todos os pedidos
            pedido liberado (SITUACAO_VENDA = 0)
            's' - liberado
            'n' - não liberado
    """
    def argdef(arg, default):
        return arg_def(kwargs, arg, default)

    empresa = argdef('empresa', 1)
    pedido = argdef('pedido', None)
    ref = argdef('ref', None)
    modelo = argdef('modelo', None)
    periodo = argdef('periodo', None)
    cancelado = argdef('cancelado', 't')
    faturado = argdef('faturado', 't')
    faturavel = argdef('faturavel', 't')
    solicitado = argdef('solicitado', 't')
    agrupado = argdef('agrupado', 't')
    pedido_liberado = argdef('pedido_liberado', 't')

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

    if agrupado == 't':
        filtro_agrupado = ''
    else:
        exists = 'NOT' if agrupado == 'n' else ''
        filtro_agrupado = f"""--
            AND {exists} EXISTS
                ( SELECT
                    1
                  FROM PEDI_110 iped -- item de pedido de venda
                  WHERE iped.PEDIDO_VENDA = i.PEDIDO_VENDA
                    AND iped.AGRUPADOR_PRODUCAO <> 0
                )
        """

    if pedido_liberado == 's':
        filtro_pedido_liberado = """--
            AND ped.SITUACAO_VENDA = 0
        """
    elif pedido_liberado == 'n':
        filtro_pedido_liberado = """--
            AND ped.SITUACAO_VENDA <> 0
        """
    else:
        filtro_pedido_liberado = ''

    sql=f"""
        SELECT
          i.CD_IT_PE_GRUPO REF
        , i.CD_IT_PE_ITEM COR
        , i.CD_IT_PE_SUBGRUPO TAM
        , t.ORDEM_TAMANHO ORDEM_TAM
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
          {filtro_faturado} -- filtro_faturado
          {filtro_faturavel} -- filtro_faturavel
          {filtro_solicitado} -- filtro_solicitado
          {filtro_agrupado} -- filtro_agrupado
          {filtro_pedido_liberado} -- filtro_pedido_liberado
        GROUP BY
          i.CD_IT_PE_GRUPO
        , i.CD_IT_PE_ITEM
        , i.CD_IT_PE_SUBGRUPO
        , t.ORDEM_TAMANHO
    """

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    return dados
