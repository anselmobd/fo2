from datetime import (
    timedelta,
)
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(
        cursor,
        data_de=None,
    ):

    data_ate = data_de + timedelta(days=1)

    filtra_data_de = f"""--
        AND ( 
          ( bt.DATA_TERMINO = DATE '{data_de}'
            AND bt.HORA_TERMINO >= TIMESTAMP '1989-11-16 06:00:00'
          )
          OR 
          ( bt.DATA_TERMINO > DATE '{data_de}'
          AND bt.DATA_TERMINO < DATE '{data_ate}'
          )
          OR 
          ( bt.DATA_TERMINO = DATE '{data_ate}'
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
