from datetime import timedelta
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import lm

from beneficia.queries import ob_destinos


__all__ = ['query']


def query(
        cursor,
        data_de=None,
        data_ate=None,
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

    filtra_data_de = ''
    if data_de:
        filtra_data_de = f"""\
            AND ( 
              ( bt.DATA_TERMINO = DATE '{data_de}'
                AND bt.HORA_TERMINO >= TIMESTAMP '1989-11-16 06:00:00'
              )
              OR
              bt.DATA_TERMINO > DATE '{data_de}'
            ) \
        """

    filtra_data_ate = ''
    if data_ate:
        data_ate = data_ate + timedelta(days=1)
        filtra_data_ate = f"""\
            AND ( 
            bt.DATA_TERMINO < DATE '{data_ate}'
            OR 
            ( bt.DATA_TERMINO = DATE '{data_ate}'
                AND bt.HORA_TERMINO < TIMESTAMP '1989-11-16 06:00:00'
            )
            ) \
        """

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
        WITH 
          bt_max_op AS 
        ( SELECT
            bt.ORDEM_PRODUCAO
          , MAX(bt.SEQ_OPERACAO) MAX_SEQ_OPERACAO
          FROM pcpb_040 bt
          JOIN PCPB_020 t
            ON t.ORDEM_PRODUCAO = bt.ORDEM_PRODUCAO
          WHERE 1=1
            AND bt.DATA_TERMINO IS NOT NULL
            {filtra_data_de} -- filtra_data_de
            {filtra_data_ate} -- filtra_data_ate
            {filtra_tipo} -- filtra_tipo
          GROUP BY 
            bt.ORDEM_PRODUCAO
        )
        , bt_prox_op AS 
        ( SELECT 
            bmo.ORDEM_PRODUCAO
          , bmo.MAX_SEQ_OPERACAO
          , MIN(bt.SEQ_OPERACAO) PROX_SEQ_OPERACAO
          FROM bt_max_op bmo
          JOIN pcpb_040 bt
            ON bt.ORDEM_PRODUCAO = bmo.ORDEM_PRODUCAO
           AND bt.SEQ_OPERACAO > bmo.MAX_SEQ_OPERACAO
          GROUP BY 
            bmo.ORDEM_PRODUCAO
          , bmo.MAX_SEQ_OPERACAO
        )
        SELECT DISTINCT 
          bt.ORDEM_PRODUCAO OB
        , bt.CODIGO_ESTAGIO EST
        , bt.SEQ_OPERACAO SEQ_OP
        , t.QTDE_QUILOS_REAL QUILOS
        , SUBSTR(t.PANO_SBG_GRUPO, 1, 2) TIPO_REF
        , t.PANO_SBG_GRUPO REF
        , t.PANO_SBG_ITEM COR
        FROM bt_prox_op bpo
        JOIN pcpb_010 ob
          ON ob.ORDEM_PRODUCAO = bpo.ORDEM_PRODUCAO
        JOIN pcpb_040 bt
          ON bt.ORDEM_PRODUCAO = bpo.ORDEM_PRODUCAO
         AND bt.SEQ_OPERACAO = bpo.PROX_SEQ_OPERACAO
        JOIN PCPB_020 t
          ON t.ORDEM_PRODUCAO = bt.ORDEM_PRODUCAO
        WHERE 1=1
          AND ob.COD_CANCELAMENTO = 0
          {filtra_estagio} -- filtra_estagio
        ORDER BY 
          bt.ORDEM_PRODUCAO
    ''')

    dict_tipo_tecido = {
        'TP': "Poliamida",
        'TA': "Algodão",
    }
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    ob2s = set()
    for row in dados:
        row['tipo_tecido'] = dict_tipo_tecido.get(row['tipo_ref'], "Desconhecido")
        ob2s.add(row['ob'])

    if ob2s:
        dest_ob2s = ob_destinos.query(cursor, ob=tuple(ob2s))

        ob2_ops = {}
        for row in dest_ob2s:
            op = row.get('op')
            if op:
                ob = row['ob']
                try:
                    ob2_ops[ob].add(op)
                except KeyError:
                    ob2_ops[ob] = {op}

        for row in dados:
            ops = ob2_ops.get(row['ob'])
            if ops:
                row['op'] = ', '.join(tuple(ops))

    return dados
