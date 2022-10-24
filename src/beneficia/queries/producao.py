from datetime import (
    date,
    timedelta,
)
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(
        cursor,
        data_de=None,
        data_ate=None,
    ):

    if not data_de:
        data_de = date.today()

    data_ate_prox = data_ate if data_ate else data_de
    data_ate_prox = data_ate_prox + timedelta(days=1)

    filtra_data_de = f"""--
        AND ( 
          ( bt.DATA_TERMINO = DATE '{data_de}'
            AND bt.HORA_TERMINO >= TIMESTAMP '1989-11-16 06:00:00'
          )
          OR 
          ( bt.DATA_TERMINO > DATE '{data_de}'
          AND bt.DATA_TERMINO < DATE '{data_ate_prox}'
          )
          OR 
          ( bt.DATA_TERMINO = DATE '{data_ate_prox}'
            AND bt.HORA_TERMINO < TIMESTAMP '1989-11-16 06:00:00'
          )
        )
    """

    sql = f'''
        SELECT
          ORDEM_PRODUCAO OB
        , SEQ_ESTAGIO SEQ_EST
        , CODIGO_ESTAGIO EST
        , SEQ_OPERACAO SEQ_OP
        , DATA_INICIO DT_INI
        , HORA_INICIO H_INI
        , DATA_TERMINO DT_FIM
        , HORA_TERMINO H_FIM
        , TURNO_PRODUCAO TURNO
        , bt.CODIGO_USUARIO COD_USU
        , ufim.USUARIO USUARIO
        FROM pcpb_040 bt
        LEFT JOIN HDOC_030 ufim -- usuários
          ON ufim.CODIGO_USUARIO = bt.CODIGO_USUARIO
        WHERE 1=1
          {filtra_data_de} -- filtra_data_de
        ORDER BY
          DATA_TERMINO
        , TURNO_PRODUCAO
        , ORDEM_PRODUCAO
        , SEQ_ESTAGIO
    '''

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)
    return dados
