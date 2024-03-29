from pprint import pprint

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute


def query(cursor, data_de, data_ate, colecao, detalhe):

    filtra_data_de = f"""--
        AND o.DATA_ENTRADA_CORTE >= '{data_de}'
    """ if data_de else ''

    filtra_data_ate = f"""--
        AND o.DATA_ENTRADA_CORTE <= '{data_ate}'
    """ if data_ate else ''

    filtra_colecao = f"""--
        AND r.COLECAO = '{colecao}'
    """ if colecao else ''


    if detalhe == 'ref':
        fields = """--
              lote.PROCONF_GRUPO REF
            , r.COLECAO || '-' || cole.DESCR_COLECAO COLECAO
        """
    elif detalhe == 'item':
        fields = """--
              lote.PROCONF_GRUPO REF
            , r.COLECAO || '-' || cole.DESCR_COLECAO COLECAO
            , lote.PROCONF_ITEM COR
            , lote.PROCONF_SUBGRUPO TAM
        """
    elif detalhe == 'col':
        fields = """--
            r.COLECAO || '-' || cole.DESCR_COLECAO COLECAO
        """

    filtra_qtdop = """--
        AND l.PROCONF_ITEM = lote.PROCONF_ITEM
        AND l.PROCONF_SUBGRUPO = lote.PROCONF_SUBGRUPO
    """ if detalhe == 'item' else ''

    if detalhe == 'ref':
        group_order = """--
              lote.PROCONF_GRUPO
            , r.COLECAO
            , cole.DESCR_COLECAO
        """
    elif detalhe == 'item':
        group_order = """--
              lote.PROCONF_GRUPO
            , r.COLECAO
            , cole.DESCR_COLECAO
            , lote.PROCONF_ITEM
            , tam.ORDEM_TAMANHO
            , lote.PROCONF_SUBGRUPO
        """
    elif detalhe == 'col':
        group_order = """--
              r.COLECAO
            , cole.DESCR_COLECAO
        """

    sql = f"""
        SELECT
          {fields} -- fields
        , lote.ORDEM_PRODUCAO OP
        , sum(lote.QTDE_PERDAS ) QTD
        , ( SELECT
              SUM( l.QTDE_PECAS_PROG )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
              {filtra_qtdop} -- filtra_totop
              AND l.SEQUENCIA_ESTAGIO = 1
          ) QTDOP
        FROM PCPC_040 lote
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
        JOIN basi_030 r
          ON r.NIVEL_ESTRUTURA = 1
         AND r.REFERENCIA = o.REFERENCIA_PECA
        JOIN BASI_140 cole
          ON cole.COLECAO = r.COLECAO
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
        WHERE 1=1
          {filtra_data_de} --  filtra_data_de
          {filtra_data_ate} --  filtra_data_ate
          {filtra_colecao} --  filtra_colecao
        GROUP BY
          {group_order} -- group_order
        , lote.ORDEM_PRODUCAO
        HAVING
          sum(lote.QTDE_PERDAS ) > 0
        ORDER BY
          {group_order} -- group_order
        , lote.ORDEM_PRODUCAO
    """

    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
