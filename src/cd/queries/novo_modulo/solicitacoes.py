from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


def get_solicitacoes(
  cursor,
  solicitacao=None,
  pedido_destino=None,
  ref_destino=None,
  ref_reservada=None,
):
    filtra_solicitacao = f"""--
        AND sl.SOLICITACAO = {solicitacao}
    """ if solicitacao else ''

    filtra_pedido_destino = f"""--
        AND sl.PEDIDO_DESTINO = {pedido_destino}
    """ if pedido_destino else ''

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
        FROM pcpc_044 sl -- solicitação / lote 
        LEFT JOIN PCPC_040 l
          ON l.QTDE_EM_PRODUCAO_PACOTE > 0
         AND l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
        WHERE sl.SOLICITACAO IS NOT NULL 
          {filtra_solicitacao} -- filtra_solicitacao
          {filtra_pedido_destino} -- filtra_pedido_destino
          {filtra_ref_destino} -- filtra_ref_destino
          {filtra_ref_reservada} -- filtra_ref_reservada
        GROUP BY 
          sl.SOLICITACAO
        ORDER BY 
          sl.SOLICITACAO 
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def get_solicitacao(cursor, id):
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
        FROM pcpc_044 sl -- solicitação / lote 
        LEFT JOIN PCPC_040 lest
          ON lest.QTDE_EM_PRODUCAO_PACOTE > 0
         AND lest.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND lest.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
        LEFT JOIN PCPC_040 l
          ON l.SEQUENCIA_ESTAGIO = 1
         AND l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
        WHERE sl.SOLICITACAO  = {id}
        ORDER BY
          sl.SITUACAO
        , lest.CODIGO_ESTAGIO
        , sl.ORDEM_PRODUCAO
        , sl.ORDEM_CONFECCAO
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist(cursor)

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
