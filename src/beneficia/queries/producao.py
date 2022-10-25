from datetime import (
    date,
    timedelta,
)
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import lm

__all__ = ['query']


def query(
        cursor,
        data_de=None,
        data_ate=None,
        turno=None,
        estagio=None,
        tipo=None
    ):
    """
    Onde:
        tipo:
            None = todos
            OB1
            OB2
    """
    if not data_de:
        data_de = date.today()

    data_ate_prox = data_ate if data_ate else data_de
    data_ate_prox = data_ate_prox + timedelta(days=1)

    filtra_data_de = f"""\
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
        ) \
    """

    filtra_turno = f"""\
        AND bt.TURNO_PRODUCAO = {turno} \
    """ if turno else ''

    filtra_estagio = f"""\
        AND bt.CODIGO_ESTAGIO = {estagio} \
    """ if estagio else ''

    if tipo:
        if tipo in ['OB1', '1', 1]:
            filtra_tipo = """\
                AND t.PANO_SBG_SUBGRUPO = 'INT' -- OB1 \
            """
        elif tipo in ['OB2', '2', 2]:
            filtra_tipo = """\
                AND t.PANO_SBG_SUBGRUPO = 'TIN' -- OB2 \
            """
    else:
        filtra_tipo = ''


    sql = lm(f'''
        SELECT DISTINCT
          bt.ORDEM_PRODUCAO OB
        , bt.SEQ_ESTAGIO SEQ_EST
        , bt.CODIGO_ESTAGIO EST
        , bt.SEQ_OPERACAO SEQ_OP
        , bt.DATA_INICIO DT_INI
        , bt.HORA_INICIO H_INI
        , bt.DATA_TERMINO DT_FIM
        , bt.HORA_TERMINO H_FIM
        , bt.TURNO_PRODUCAO TURNO
        , bt.CODIGO_USUARIO COD_USU
        , ufim.USUARIO USUARIO
        , t.QTDE_QUILOS_REAL QUILOS
        , SUBSTR(t.PANO_SBG_GRUPO, 1, 2) TIPO_REF
        , t.PANO_SBG_GRUPO REF
        , t.PANO_SBG_ITEM COR
        , b.GRUPO_MAQUINA GRUP_MAQ
        , b.SUBGRUPO_MAQUINA SUB_MAQ 
        , b.NUMERO_MAQUINA NUM_MAQ
        FROM pcpb_040 bt
        LEFT JOIN HDOC_030 ufim -- usuários
          ON ufim.CODIGO_USUARIO = bt.CODIGO_USUARIO
        JOIN PCPB_010 b
          ON b.ORDEM_PRODUCAO = bt.ORDEM_PRODUCAO
        JOIN PCPB_020 t
          ON t.ORDEM_PRODUCAO = bt.ORDEM_PRODUCAO
        WHERE 1=1
          {filtra_data_de} -- filtra_data_de
          {filtra_turno} -- filtra_turno
          {filtra_estagio} -- filtra_estagio
          {filtra_tipo} -- filtra_tipo
        ORDER BY
          bt.DATA_TERMINO
        , bt.TURNO_PRODUCAO
        , SUBSTR(t.PANO_SBG_GRUPO, 1, 2)
        , bt.ORDEM_PRODUCAO
        , bt.SEQ_ESTAGIO
    ''')

    dict_tipo_tecido = {
        'TP': "Poliamida",
        'TA': "Algodão",
    }
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)
    for row in dados:
        row['maq'] = f"{row['grup_maq']}.{row['sub_maq']}.{row['num_maq']:05}"
        row['tipo_tecido'] = dict_tipo_tecido.get(row['tipo_ref'], "Desconhecido")
    return dados
