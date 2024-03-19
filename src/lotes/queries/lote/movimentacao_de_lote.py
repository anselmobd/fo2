from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import lms


def insere(cursor, lote, estagio, qtd, estagio_modelo=None):
    estagio_modelo = estagio_modelo if estagio_modelo else estagio
    sql = lms(f"""\
        INSERT INTO SYSTEXTIL.PCPC_045
        ( PCPC040_PERCONF, PCPC040_ORDCONF, PCPC040_ESTCONF, SEQUENCIA
        , DATA_PRODUCAO, HORA_PRODUCAO, QTDE_PRODUZIDA, QTDE_PECAS_2A
        , QTDE_CONSERTO, TURNO_PRODUCAO, TIPO_ENTRADA_ORD, NOTA_ENTR_ORDEM
        , SERIE_NF_ENT_ORD, SEQ_NF_ENTR_ORD, ORDEM_PRODUCAO, CODIGO_USUARIO
        , QTDE_PERDAS, NUMERO_DOCUMENTO, CODIGO_DEPOSITO, CODIGO_FAMILIA
        , CODIGO_INTERVALO, EXECUTA_TRIGGER, DATA_INSERCAO, PROCESSO_SYSTEXTIL
        , NUMERO_VOLUME, NR_OPERADORES, ATZ_PODE_PRODUZIR, ATZ_EM_PROD
        , ATZ_A_PROD, EFICIENCIA_INFORMADA, USUARIO_SYSTEXTIL, CODIGO_OCORRENCIA
        , COD_OCORRENCIA_ESTORNO, SOLICITACAO_CONSERTO, NUMERO_SOLICITACAO
        , NUMERO_ORDEM, MINUTOS_PECA, NR_OPERADORES_INFORMADO, EFICIENCIA
        )
        WITH movimentos_estagio AS 
        ( SELECT
            ml.PCPC040_PERCONF
          , ml.PCPC040_ORDCONF
          , {estagio} -- ml.PCPC040_ESTCONF
          , ml.SEQUENCIA+1
          , CURRENT_DATE DATA_PRODUCAO
          , CURRENT_DATE HORA_PRODUCAO
          , {qtd} -- ml.QTDE_PRODUZIDA
          , ml.QTDE_PECAS_2A
          , ml.QTDE_CONSERTO
          , 1 -- ml.TURNO_PRODUCAO
          , 0 -- ml.TIPO_ENTRADA_ORD
          , ml.NOTA_ENTR_ORDEM
          , NULL -- ml.SERIE_NF_ENT_ORD
          , ml.SEQ_NF_ENTR_ORD
          , ml.ORDEM_PRODUCAO
          , 1 -- ml.CODIGO_USUARIO
          , ml.QTDE_PERDAS
          , ml.NUMERO_DOCUMENTO
          , ml.CODIGO_DEPOSITO
          , ml.CODIGO_FAMILIA
          , ml.CODIGO_INTERVALO
          , ml.EXECUTA_TRIGGER
          , CURRENT_DATE -- ml.DATA_INSERCAO
          , NULL -- ml.PROCESSO_SYSTEXTIL
          , ml.NUMERO_VOLUME
          , 0 -- ml.NR_OPERADORES
          , ml.ATZ_PODE_PRODUZIR
          , ml.ATZ_EM_PROD
          , ml.ATZ_A_PROD
          , ml.EFICIENCIA_INFORMADA
          , NULL -- ml.USUARIO_SYSTEXTIL
          , ml.CODIGO_OCORRENCIA
          , ml.COD_OCORRENCIA_ESTORNO
          , ml.SOLICITACAO_CONSERTO
          , ml.NUMERO_SOLICITACAO
          , ml.NUMERO_ORDEM
          , ml.MINUTOS_PECA
          , ml.NR_OPERADORES_INFORMADO
          , ml.EFICIENCIA
          FROM PCPC_045 ml
          WHERE 1=1
            AND ml.PCPC040_PERCONF = {lote[:4]}
            AND ml.PCPC040_ORDCONF = {lote[4:]}
            AND ml.PCPC040_ESTCONF = {estagio_modelo}
          ORDER BY 
            ml.SEQUENCIA DESC
        )
        SELECT 
          *
        FROM movimentos_estagio
        WHERE rownum = 1
    """)
    debug_cursor_execute(cursor, sql)


def get_movimentacoes(cursor, lote, estagio):
    sql = lms(f"""\
        SELECT
          ml.*
        FROM PCPC_045 ml
        WHERE ml.PCPC040_PERCONF = {lote[:4]}
          AND ml.PCPC040_ORDCONF = {lote[4:]}
          AND ml.PCPC040_ESTCONF = {estagio}
        ORDER BY 
          ml.SEQUENCIA
    """)
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)

