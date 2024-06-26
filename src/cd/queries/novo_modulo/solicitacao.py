from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def existe_solicitacao(
    cursor,
    solicitacao,
):
    sql = f"""
        SELECT DISTINCT
          sl.SOLICITACAO
        FROM pcpc_044 sl -- solicitação / lote
        WHERE sl.SOLICITACAO = {solicitacao}
    """
    debug_cursor_execute(cursor, sql)
    return len(dictlist_lower(cursor)) != 0


def get_solicitacao(
    cursor,
    solicitacao=None,
    pedido_destino=None,
    ref_destino=None,
    ref_reservada=None,
    op=None,
    lote=None,
    situacao=None,
    order='sit_oc'
):
    """
        order:
            'sit_oc' = situação, estágio, OP e OC
            'rota_end' = rota, endereço, OP e OC
    """
    if not solicitacao or solicitacao == '-':
        filtra_solicitacao = "AND sl.SOLICITACAO IS NULL"
    elif solicitacao != '!':
        filtra_solicitacao = f"AND sl.SOLICITACAO = {solicitacao}"
    else:
        filtra_solicitacao = ''

    filtra_pedido_destino = f"""--
        AND sl.PEDIDO_DESTINO = {pedido_destino}
    """ if pedido_destino else ''

    filtra_ref_destino = f"""--
        AND sl.GRUPO_DESTINO = '{ref_destino}'
    """ if ref_destino else ''

    filtra_ref_reservada = f"""--
        AND l.PROCONF_GRUPO = '{ref_reservada}'
    """ if ref_reservada else ''

    filtra_op = f"""--
        AND sl.ORDEM_PRODUCAO = '{op}'
    """ if op else ''

    filtra_lote = ''
    if lote:
        if not isinstance(lote, (tuple, list)):
            lote = [lote]
        cada_lote = [
            f"((l.PERIODO_PRODUCAO * 100000) + sl.ORDEM_CONFECCAO = {cada_lote})\n"
            for cada_lote in lote
        ]
        filtra_lote = " OR ".join(cada_lote)
        filtra_lote = f" AND ( {filtra_lote} )"

    filtra_situacao = ''
    if situacao:
        if not isinstance(situacao, (tuple, list)):
            situacao = [situacao]
        cada_situacao = [
            f"(sl.SITUACAO = '{s}')\n"
            for s in situacao
        ]
        filtra_situacao = " OR ".join(cada_situacao)
        filtra_situacao = f" AND ( {filtra_situacao} )"

    if order == 'sit_oc':
        order_by = """--
              sl.SITUACAO
            , lest.CODIGO_ESTAGIO
            , sl.ORDEM_PRODUCAO
            , sl.ORDEM_CONFECCAO
        """
    elif order == 'rota_end':
        order_by = """--
              COALESCE(e.ROTA, '-')
            , COALESCE(ec.COD_ENDERECO, '-')
            , sl.ORDEM_PRODUCAO
            , sl.ORDEM_CONFECCAO
        """

    # campos marcados com "--" são primary key
    sql = f"""
        SELECT DISTINCT
          sl.ORDEM_PRODUCAO --
        , sl.ORDEM_CONFECCAO --
        , sl.PEDIDO_DESTINO --
        , sl.OP_DESTINO --
        , sl.OC_DESTINO --
        , sl.DEP_DESTINO --
        , sl.QTDE
        , sl.SITUACAO
        , sl.SOLICITACAO
        , sl.PERIODO_OC
        , sl.GRUPO_DESTINO --
        , sl.ALTER_DESTINO --
        , sl.SUB_DESTINO --
        , sl.COR_DESTINO --
        , sl.INCLUSAO
        , lest.CODIGO_ESTAGIO
        , l.PERIODO_PRODUCAO PERIODO
        , l.PROCONF_NIVEL99 NIVEL
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , l.QTDE_PECAS_PROG QTD_ORI
        , CASE WHEN lp.COD_CONTAINER IS NOT NULL
                AND lp.COD_CONTAINER <> '0'
          THEN lp.COD_CONTAINER
          ELSE '-'
          END palete
        , CASE WHEN lp.COD_CONTAINER IS NOT NULL
                AND lp.COD_CONTAINER <> '0'
          THEN lp.DATA_INCLUSAO
          ELSE NULL
          END inclusao_palete
        , COALESCE(ec.COD_ENDERECO, '-') endereco
        , ec.DATA_INCLUSAO inclusao_endereco
        , COALESCE(e.ROTA, '-') rota
        FROM pcpc_044 sl -- solicitação / lote
        -- Na tabela de solicitações aparece a OP de expedição também como
        -- reservada, com situação 4. Para tentar evitar isso, não listo
        -- lotes que pertençam a OP que não tem estágio 63
        -- (OPs de expedição não tem 63)
        JOIN PCPC_040 l_filtro
          ON l_filtro.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND l_filtro.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
         AND l_filtro.CODIGO_ESTAGIO = 63
        LEFT JOIN PCPC_040 lest
          -- ON lest.QTDE_EM_PRODUCAO_PACOTE > 0
          ON lest.SEQUENCIA_ESTAGIO = (
            SELECT
              MIN(lest2.SEQUENCIA_ESTAGIO)
            FROM PCPC_040 lest2
            WHERE 1=1
              AND lest2.QTDE_EM_PRODUCAO_PACOTE > 0
              AND lest2.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
              AND lest2.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
          )
         AND lest.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND lest.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
        LEFT JOIN PCPC_040 l
          ON l.SEQUENCIA_ESTAGIO = 1
         AND l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
        LEFT JOIN ENDR_014 lp -- lote/palete - oc/container
          ON lp.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND lp.ORDEM_CONFECCAO = (l.PERIODO_PRODUCAO * 100000) + sl.ORDEM_CONFECCAO
        LEFT JOIN ENDR_015 ec -- endereço/container
          ON ec.COD_CONTAINER = lp.COD_CONTAINER
        LEFT JOIN ENDR_013 e -- endereço
          ON e.COD_ENDERECO = ec.COD_ENDERECO
        WHERE 1=1
          {filtra_solicitacao} -- filtra_solicitacao
          {filtra_pedido_destino} -- filtra_pedido_destino
          {filtra_ref_destino} -- filtra_ref_destino
          {filtra_ref_reservada} -- filtra_ref_reservada
          {filtra_op} -- filtra_op
          {filtra_lote} -- filtra_lote
          {filtra_situacao} -- filtra_situacao
        ORDER BY
          {order_by} -- order_by
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        row['lote'] = '{}{:05}'.format(row['periodo'], row['ordem_confeccao'])
        if not row['codigo_estagio']:
            row['codigo_estagio'] = 'Finalizado'
        row['int_parc'] = 'inteiro' if row['qtde'] == row['qtd_ori'] else 'parcial'
        row['grupo_destino_ori'] = row['grupo_destino']
        row['sub_destino_ori'] = row['sub_destino']
        row['cor_destino_ori'] = row['cor_destino']
        if row['grupo_destino'] == '00000':
            row['grupo_destino'] = row['ref']
        if row['sub_destino'] == '0':
            row['sub_destino'] = row['tam']
        if row['cor_destino'] == '0':
            row['cor_destino'] = row['cor']

    return dados
