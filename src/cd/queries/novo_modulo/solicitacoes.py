from pprint import pprint
from typing import Iterable

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def get_solicitacoes(
    cursor,
    solicitacao=None,
    pedido_destino=None,
    ref_destino=None,
    ref_reservada=None,
    lote=None,
    op=None,
    com_lotes_situacao_de=None,
    com_lotes_situacao_ate=None,
    # sem_lotes_situacao_de=None,
    # sem_lotes_situacao_ate=None,
    desc=False,
):
    filtra_solicitacao = f"""--
        AND sl.SOLICITACAO = {solicitacao}
    """ if solicitacao else ''

    if pedido_destino:
        if isinstance(pedido_destino, (tuple, list)):
            condicao = ", ".join(map(str, pedido_destino))
            condicao = f" IN ({condicao})"
        else:
            condicao = f"= {pedido_destino}"
        filtra_pedido_destino = f"""--
            AND sl.PEDIDO_DESTINO {condicao}
        """
    else:
        filtra_pedido_destino = ""

    filtra_ref_destino = f"""--
        AND ( ( sl.GRUPO_DESTINO = '00000'
              AND l.PROCONF_GRUPO = '{ref_destino}'
              )
            OR sl.GRUPO_DESTINO = '{ref_destino}'
            )
    """ if ref_destino else ''

    filtra_ref_reservada = f"""--
        AND l.PROCONF_GRUPO = '{ref_reservada}'
    """ if ref_reservada else ''

    filtra_lote = ''
    if lote:
        filtra_lote = f"""--
            AND l_filtro.PERIODO_PRODUCAO = {lote[:4]}
            AND l_filtro.ORDEM_CONFECCAO = {lote[4:]}
        """
    
    filtra_op = f"""--
        AND sl.ORDEM_PRODUCAO = '{op}'
    """ if op else ''

    filtra_com_lotes_situacao_de = f"""--
        AND sl.SITUACAO >= '{com_lotes_situacao_de}'
    """ if com_lotes_situacao_de and com_lotes_situacao_de.isdigit() else ''

    filtra_com_lotes_situacao_ate = f"""--
        AND sl.SITUACAO <= '{com_lotes_situacao_ate}'
    """ if com_lotes_situacao_ate and com_lotes_situacao_ate.isdigit() else ''

    if (
        filtra_pedido_destino
        # or filtra_ref_destino
        # or filtra_ref_reservada
        or filtra_lote
        or filtra_op
    ):
        solicitacao_nula = ""
    else:
        solicitacao_nula = "AND sl.SOLICITACAO IS NOT NULL"

    sql = f"""
        SELECT DISTINCT
          sl.SOLICITACAO 
        , sum(CASE WHEN sl.SITUACAO = 1 THEN 1 ELSE 0 END) l1
        , sum(CASE WHEN sl.SITUACAO = 1 THEN sl.QTDE ELSE 0 END) q1
        , sum(CASE WHEN sl.SITUACAO = 2 THEN 1 ELSE 0 END) l2
        , sum(CASE WHEN sl.SITUACAO = 2 THEN sl.QTDE ELSE 0 END) q2
        , sum(CASE WHEN sl.SITUACAO = 3 THEN 1 ELSE 0 END) l3
        , sum(CASE WHEN sl.SITUACAO = 3 THEN sl.QTDE ELSE 0 END) q3
        , sum(CASE WHEN sl.SITUACAO = 4 THEN 1 ELSE 0 END) l4
        , sum(CASE WHEN sl.SITUACAO = 4 THEN sl.QTDE ELSE 0 END) q4
        , sum(CASE WHEN sl.SITUACAO = 5 THEN 1 ELSE 0 END) l5
        , sum(CASE WHEN sl.SITUACAO = 5 THEN sl.QTDE ELSE 0 END) q5
        , sum(CASE WHEN l.CODIGO_ESTAGIO IS NULL THEN 1 ELSE 0 END) lf
        , sum(CASE WHEN l.CODIGO_ESTAGIO IS NULL THEN sl.QTDE ELSE 0 END) qf
        , sum(CASE WHEN l.CODIGO_ESTAGIO IS NOT NULL THEN 1 ELSE 0 END) lp
        , sum(CASE WHEN l.CODIGO_ESTAGIO IS NOT NULL THEN sl.QTDE ELSE 0 END) qp
        , sum(1) lt
        , sum(sl.QTDE) qt
        , max(sl.INCLUSAO) inclusao
        , LISTAGG(DISTINCT sl.PEDIDO_DESTINO, ', ')
          WITHIN GROUP (ORDER BY sl.PEDIDO_DESTINO) pedidos_destino
        FROM pcpc_044 sl -- solicitação / lote 
        -- Na tabela de solicitações aparece a OP de expedição também como
        -- reservada, com situação 4. Para tentar evitar isso, não listo
        -- lotes que pertençam a OP que não tem estágio 63
        -- (OPs de expedição não tem 63)
        JOIN PCPC_040 l_filtro
          ON l_filtro.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND l_filtro.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
         AND l_filtro.CODIGO_ESTAGIO = 63
        LEFT JOIN PCPC_040 l
          ON l.QTDE_EM_PRODUCAO_PACOTE > 0
         AND l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
        WHERE 1=1
          {solicitacao_nula} -- solicitacao_nula
          {filtra_solicitacao} -- filtra_solicitacao
          {filtra_pedido_destino} -- filtra_pedido_destino
          {filtra_ref_destino} -- filtra_ref_destino
          {filtra_ref_reservada} -- filtra_ref_reservada
          {filtra_lote} -- filtra_lote
          {filtra_op} -- filtra_op
          {filtra_com_lotes_situacao_de} -- filtra_com_lotes_situacao_de
          {filtra_com_lotes_situacao_ate} -- filtra_com_lotes_situacao_ate
        GROUP BY 
          sl.SOLICITACAO
        ORDER BY 
          sl.SOLICITACAO {"DESC" if desc else ""}
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)


def get_solicitacao(
    cursor,
    solicitacao=None,
    pedido_destino=None,
    op=None,
    lote=None,
):

    if solicitacao and solicitacao != '-':
        filtra_solicitacao = f"AND sl.SOLICITACAO = {solicitacao}"
    else:
        filtra_solicitacao = "AND sl.SOLICITACAO IS NULL"

    filtra_pedido_destino = f"""--
        AND sl.PEDIDO_DESTINO = {pedido_destino}
    """ if pedido_destino else ''

    filtra_op = f"""--
        AND sl.ORDEM_PRODUCAO = '{op}'
    """ if op else ''

    filtra_lote = f"""--
        AND (l.PERIODO_PRODUCAO * 100000) + sl.ORDEM_CONFECCAO = {lote}
    """ if lote else ''

    sql = f"""
        SELECT DISTINCT
          sl.ORDEM_PRODUCAO
        , sl.ORDEM_CONFECCAO
        , sl.PEDIDO_DESTINO
        , sl.OP_DESTINO
        , sl.OC_DESTINO
        , sl.DEP_DESTINO
        , sl.QTDE
        , sl.SITUACAO
        , sl.SOLICITACAO
        , sl.PERIODO_OC
        , sl.GRUPO_DESTINO
        , sl.ALTER_DESTINO
        , sl.SUB_DESTINO
        , sl.COR_DESTINO
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
          {filtra_op} -- filtra_op
          {filtra_lote} -- filtra_lote
        ORDER BY
          sl.SITUACAO
        , lest.CODIGO_ESTAGIO
        , sl.ORDEM_PRODUCAO
        , sl.ORDEM_CONFECCAO
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        row['lote'] = '{}{:05}'.format(row['periodo'], row['ordem_confeccao'])
        if not row['codigo_estagio']:
            row['codigo_estagio'] = 'Finalizado'
        row['int_parc'] = 'Inteiro' if row['qtde'] == row['qtd_ori'] else 'parcial'
        if row['grupo_destino'] == '00000':
            row['grupo_destino'] = row['ref']
        if row['sub_destino'] == '0':
            row['sub_destino'] = row['tam']
        if row['cor_destino'] == '0':
            row['cor_destino'] = row['cor']

    return dados
