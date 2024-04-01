from pprint import pprint

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import dedent_strip


def posicao_so_estagios(cursor, periodo=None, ordem_confeccao=None, lote=None):
    periodo = periodo if lote is None else lote[:4]
    ordem_confeccao = ordem_confeccao if lote is None else lote[4:]
    sql = dedent_strip(f"""
        SELECT
          l.CODIGO_ESTAGIO COD_EST
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
        , l.QTDE_PROGRAMADA Q_PROG
        , l.QTDE_PECAS_PROG Q_P
        , l.QTDE_A_PRODUZIR_PACOTE Q_AP
        , l.QTDE_EM_PRODUCAO_PACOTE Q_EP
        , l.QTDE_DISPONIVEL_BAIXA Q_DB
        , l.QTDE_PECAS_PROD Q_PROD
        , l.QTDE_PECAS_2A Q_2A
        , l.QTDE_PERDAS Q_PERDA
        , l.QTDE_CONSERTO Q_CONSERTO
        , l.CODIGO_FAMILIA FAMI
        , l.NUMERO_ORDEM OS
        , l.SEQ_OPERACAO SEQ_OPER
        , l.SEQUENCIA_ESTAGIO SEQ_EST
        , l.ESTAGIO_ANTERIOR EST_ANT
        FROM PCPC_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.PERIODO_PRODUCAO = {periodo}
          AND l.ORDEM_CONFECCAO = {ordem_confeccao}
        ORDER BY
          l.SEQ_OPERACAO
    """)
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
