from pprint import pprint

from utils.functions import arg_def
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from cd.queries.novo_modulo.gerais import get_filtra_ref

__all__ = ['query']


def query(cursor, **kwargs):
    def argdef(arg, default):
        return arg_def(kwargs, arg, default)

    empresa = argdef('empresa', 1)  # default tussor matriz
    pedido = argdef('pedido', None)
    ref = argdef('ref', None)
    modelo = argdef('modelo', None)
    periodo = argdef('periodo', None)
    cancelado = argdef('cancelado', 't')  # default todos os pedidos
    faturado = argdef('faturado', 't')  # default todos os pedidos
    faturavel = argdef('faturavel', 't')  # default todos os pedidos
    solicitado = argdef('solicitado', 't')  # default todos os pedidos
    agrupado = argdef('agrupado', 't')  # default todos os pedidos
    pedido_liberado = argdef('pedido_liberado', 't')  # default todos os pedidos
    total = argdef('total', None)

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

    if periodo:
        periodo_list = periodo.split(':')
        if periodo_list[0] != '':
            filtra_periodo += f"""--
                AND ped.DATA_ENTR_VENDA > CURRENT_DATE + {periodo_list[0]}
            """
        if periodo_list[1] != '':
            filtra_periodo += f"""--
                AND ped.DATA_ENTR_VENDA <= CURRENT_DATE + {periodo_list[1]}
            """
    else:
        filtra_periodo = ''

    if cancelado in ['c', 'i']:  # cancelado ou inativo
        filtro_cancelado = """--
            AND ped.STATUS_PEDIDO = 5 -- cancelado
        """
    elif cancelado in ['n', 'a']:  # não cancelado ou ativo
        filtro_cancelado = """--
            AND ped.STATUS_PEDIDO <> 5 -- não cancelado
        """
    else:
        filtro_cancelado = ''

    if faturado == 'f':  # faturado
        filtro_faturado = """--
            AND f.NUM_NOTA_FISCAL IS NOT NULL -- faturado
        """
    elif faturado == 'n':  # não faturado
        filtro_faturado = """--
            AND f.NUM_NOTA_FISCAL IS NULL -- não faturado
        """
    else:
        filtro_faturado = ''

    filtro_faturavel = ''
    if faturavel == 'f':  # faturavel
        filtro_faturavel = """--
            AND fok.NUM_NOTA_FISCAL IS NULL"""
    elif faturavel == 'n':  # não faturavel
        filtro_faturavel = """--
            AND fok.NUM_NOTA_FISCAL IS NOT NULL"""

    filtro_solicitado = ''
    if solicitado == 's':  # solicitado
        filtro_solicitado = """--
            AND EXISTS
                ( SELECT
                    1
                  FROM pcpc_044 sl -- solicitação / lote 
                  WHERE sl.PEDIDO_DESTINO = i.PEDIDO_VENDA
                    AND sl.SITUACAO <> 0
                )
        """
    elif solicitado == 'n':  # não solicitado
        filtro_solicitado = """--
            AND NOT EXISTS
                ( SELECT
                    1
                  FROM pcpc_044 sl -- solicitação / lote 
                  WHERE sl.PEDIDO_DESTINO = i.PEDIDO_VENDA
                    AND sl.SITUACAO <> 0
                )
        """

    filtro_agrupado = ''
    if agrupado == 's':  # agrupado em empenho para varejo
        filtro_agrupado = """--
            AND EXISTS
                ( SELECT
                    1
                  FROM PEDI_110 iped -- item de pedido de venda
                  WHERE iped.PEDIDO_VENDA = i.PEDIDO_VENDA
                    AND iped.AGRUPADOR_PRODUCAO <> 0
                )
        """
    elif agrupado == 'n':  # agrupado em empenho para varejo
        filtro_agrupado = """--
            AND NOT EXISTS
                ( SELECT
                    1
                  FROM PEDI_110 iped -- item de pedido de venda
                  WHERE iped.PEDIDO_VENDA = i.PEDIDO_VENDA
                    AND iped.AGRUPADOR_PRODUCAO <> 0
                )
        """

    filtro_pedido_liberado = ''
    if pedido_liberado == 's':  # pedido_liberado
        filtro_pedido_liberado = """--
            AND ped.SITUACAO_VENDA = 0
        """

    # sortimento
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
