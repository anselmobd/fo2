from datetime import timedelta
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import dedent

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
              ( filt.dt = DATE '{data_de}'
                AND filt.dt >= TIMESTAMP '1989-11-16 06:00:00'
              )
              OR
              filt.dt > DATE '{data_de}'
            ) \
        """

    filtra_data_ate = ''
    if data_ate:
        data_ate = data_ate + timedelta(days=1)
        filtra_data_ate = f"""\
            AND ( 
              filt.dt < DATE '{data_ate}'
              OR 
              ( filt.dt = DATE '{data_ate}'
                AND filt.dt < TIMESTAMP '1989-11-16 06:00:00'
              )
            ) \
        """

    filtra_estagio = f"""\
        AND filt.est = {estagio} \
    """ if estagio else ''

    if tipo:
        if tipo in ['OB1', '1', 1]:
            filtra_tipo = """\
                AND tpo.PANO_SBG_SUBGRUPO = 'INT' -- OB1 \
            """
        elif tipo in ['OB2', '2', 2]:
            filtra_tipo = """\
                AND tpo.PANO_SBG_SUBGRUPO = 'TIN' -- OB2 \
            """
    else:
        filtra_tipo = ''

    # passos
    # 1: busca menor sequencia de operação não executada
    # 2: pega o código de estágio da menor sequencia e qual é
    #    a sequencia anterios, ou seja, a ultima executada
    # 3: pego a data da pendência, que pode ser da última operação
    #    executada ou, se não houver nenhuma, a data de programação
    #    da OB
    # 4: filtra por periodo de data de pendência e por estágio pendente
    # 5: busca outros dados da OB para apresentação na tela
    sql = dedent(f'''
        WITH
          ob_min_seq_null AS
        (
        SELECT 
          bt.ORDEM_PRODUCAO OB
        , MIN(bt.SEQ_OPERACAO) MIN_SEQ
        FROM pcpb_040 bt -- estágios de ordem de beneficiamento
        JOIN PCPB_010 obt -- Ordem de Beneficiamento de Tecidos (OT)
          ON obt.ORDEM_PRODUCAO = bt.ORDEM_PRODUCAO
        JOIN PCPB_020 tpo -- Tecidos a Produzir da Ordem (OB2-TIN)
          ON tpo.ORDEM_PRODUCAO = bt.ORDEM_PRODUCAO
        WHERE 1=1
          AND obt.COD_CANCELAMENTO = 0
          -- AND tpo.PANO_SBG_SUBGRUPO = 'TIN' -- OB2              -- filtra_tipo
          {filtra_tipo} -- filtra_tipo
          AND bt.DATA_TERMINO IS NULL
        GROUP BY 
          bt.ORDEM_PRODUCAO
        )
        , ob_max_seq_not_null AS
        (
        SELECT 
          omsn.OB
        , omsn.MIN_SEQ
        , btmin.CODIGO_ESTAGIO EST
        , MAX(btmax.SEQ_OPERACAO) MAX_SEQ
        FROM ob_min_seq_null omsn
        JOIN pcpb_040 btmin
          ON btmin.ORDEM_PRODUCAO = omsn.OB
         AND btmin.SEQ_OPERACAO = omsn.MIN_SEQ  
        LEFT JOIN pcpb_040 btmax
          ON btmax.ORDEM_PRODUCAO = omsn.OB
         AND btmax.SEQ_OPERACAO < omsn.MIN_SEQ  
        GROUP BY 
          omsn.OB
        , omsn.MIN_SEQ
        , btmin.CODIGO_ESTAGIO
        )
        , ob_filtrar AS
        (
        SELECT 
          omsnn.OB
        --, omsnn.MIN_SEQ
        , omsnn.EST
        , omsnn.MAX_SEQ SEQ
        , CASE WHEN omsnn.MAX_SEQ IS NULL
          THEN obt.DATA_PROGRAMA
          ELSE btmax.DATA_INICIO
          END dt
        --, obt.DATA_PROGRAMA dt_ot
        --, btmax.DATA_INICIO dt_minseq_ini
        --, btmax.DATA_TERMINO dt_minseq_fim 
        FROM ob_max_seq_not_null omsnn
        LEFT JOIN pcpb_040 btmax
          ON btmax.ORDEM_PRODUCAO = omsnn.OB
         AND btmax.SEQ_OPERACAO = omsnn.MAX_SEQ  
        JOIN PCPB_010 obt -- Ordem de Beneficiamento de Tecidos (OT)
          ON obt.ORDEM_PRODUCAO = omsnn.OB
        WHERE 1=1
        --  AND 
        ORDER BY 
          omsnn.OB DESC
        )
        , ob_pendente AS 
        (
        SELECT
          *
        FROM ob_filtrar filt
        WHERE 1=1
          -- AND ( 
          --     ( filt.dt = DATE '2022-01-01'
          --       AND filt.dt >= TIMESTAMP '1989-11-16 06:00:00'
          --     )
          --     OR
          --     filt.dt > DATE '2022-01-01'
          --   )          -- filtra_data_de
          {filtra_data_de} -- filtra_data_de
          --               AND ( 
          --   filt.dt < DATE '2024-01-01'
          --   OR 
          --   ( filt.dt = DATE '2024-01-01'
          --       AND filt.dt < TIMESTAMP '1989-11-16 06:00:00'
          --   )
          --   )          -- filtra_data_ate
          {filtra_data_ate} -- filtra_data_ate
          -- AND filt.est = 70
          {filtra_estagio} -- filtra_estagio
        )
        SELECT DISTINCT 
          obp.OB
        , obp.DT
        , obt.GRUPO_MAQUINA GRUP_MAQ
        , obt.SUBGRUPO_MAQUINA SUB_MAQ 
        , obt.NUMERO_MAQUINA NUM_MAQ
        , obp.EST
        , eob.SEQ_OPERACAO SEQ_OP
        , tpo.QTDE_QUILOS_REAL QUILOS
        , SUBSTR(tpo.PANO_SBG_GRUPO, 1, 2) TIPO_REF
        , tpo.PANO_SBG_GRUPO REF
        , tpo.PANO_SBG_ITEM COR
        FROM ob_pendente obp
        LEFT JOIN PCPB_010 obt -- Ordem de Beneficiamento de Tecidos (OT)
          ON obt.ORDEM_PRODUCAO = obp.OB
        LEFT JOIN pcpb_040 eob -- estágios de ordem de beneficiamento
          ON eob.ORDEM_PRODUCAO = obp.OB
         AND eob.CODIGO_ESTAGIO = obp.EST
        LEFT JOIN PCPB_020 tpo -- Tecidos a Produzir da Ordem (OB2-TIN)
          ON tpo.ORDEM_PRODUCAO = obp.OB
        ORDER BY 
          obp.OB
    ''')

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    dict_tipo_tecido = {
        'TP': "Poliamida",
        'TA': "Algodão",
    }
    ob2s = set()
    for row in dados:
        row['maq'] = f"{row['grup_maq']} {row['sub_maq']} {row['num_maq']:05}"
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
