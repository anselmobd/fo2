from pprint import pprint

from utils.functions.models.dictlist import (
    dictlist_lower, 
    dictlist_split,
)
from utils.functions.queries import (
    debug_cursor_execute,
    sql_where_none_if,
)
from utils.functions.strings import (
    split_numbers,
)

from produto.functions import item_str

import lotes.queries

__all__ = ['query']


def append_ordem_test(lista, comp, ordem):
    lista.append(" ".join(["b.ORDEM_PRODUCAO", comp, ordem]))


def query(
        cursor,
        periodo=None,
        data=None,
        selecao='s',
    ):

    filtra_periodo = sql_where_none_if("pe.PERIODO_PRODUCAO", periodo)

    filtra_data_ini = sql_where_none_if("pe.DATA_INI_PERIODO", str(data), 'None', operation="<=")
    filtra_data_fim = sql_where_none_if("pe.DATA_FIM_PERIODO", str(data), 'None', operation=">=")

    having_selecao = """ --
        HAVING 
          count(*)
          > sum(
            CASE WHEN p.PESO_REAL = 0 THEN 0 ELSE 1 END
          )
    """ if selecao == 's' else ''

    sql = f'''
        WITH a_pesar AS 
        (
          SELECT 
            p.ORDEM_PRODUCAO OT
          , count(*) pesar
          , sum(
              CASE WHEN p.PESO_REAL = 0 THEN 0 ELSE 1 END
            ) pesados
          FROM PCPB_080 p
          WHERE 1=1
            AND p.PESAR_PRODUTO = 1
            AND p.PESO_PREVISTO > 0
          GROUP BY 
            p.ORDEM_PRODUCAO
          {having_selecao} -- having_selecao
          ORDER BY 
            p.ORDEM_PRODUCAO DESC 
        )
        , ord_t AS
        ( SELECT
            ap.ot
          , ot.ORDEM_PRODUCAO OB
          FROM a_pesar ap
          JOIN PCPB_100 ot
            ON ot.ORDEM_AGRUPAMENTO = ap.ot
        )
        , ord_dest AS
        ( SELECT
            ord_t.ot
          , ord_t.ob
          , min(ob1.NR_PEDIDO_ORDEM) ob1
          FROM ord_t
          JOIN pcpb_030 ob1
            ON ob1.ORDEM_PRODUCAO = ord_t.ob
          GROUP BY 
            ord_t.ot
          , ord_t.ob
        )
        , ord_b1 AS
        ( SELECT
            od.ot
          , od.ob
          , od.ob1
          , ob.PERIODO_PRODUCAO per
          , ob.OBSERVACAO obs
          FROM ord_dest od
          JOIN PCPB_010 ob
            ON ob.ORDEM_PRODUCAO = od.ob1
        )
        , period as
        ( SELECT 
            pe.PERIODO_PRODUCAO per
          , pe.DATA_INI_PERIODO dtini
          , pe.DATA_FIM_PERIODO dtfim
          FROM PCPC_010 pe -- períodos
          WHERE 1=1
            {filtra_periodo} -- filtra_periodo
            {filtra_data_ini} -- filtra_data_ini
            {filtra_data_fim} -- filtra_data_fim
            AND pe.AREA_PERIODO = 2 -- beneficiamento
        )
        SELECT 
          ob.ot
        , p.SEQUENCIA_ESTRUTURA seq
        , ob.ob
        , ob.ob1
        , pe.per
        , pe.dtini
        , pe.dtfim
        , ob.obs
        , p.NIVEL_COMP nivel
        , p.GRUPO_COMP ref
        , p.SUBGRUPO_COMP tam
        , p.ITEM_COMP cor
        , p.PESO_PREVISTO p_previsto
        , p.PESO_REAL p_real
        FROM ord_b1 ob
        JOIN period pe
          ON 1=1
        JOIN PCPB_080 p
          ON p.ORDEM_PRODUCAO = ob.ot
        WHERE 1=1
          AND p.PESAR_PRODUTO = 1
          AND p.PESO_PREVISTO > 0
          AND ob.per = pe.per
        UNION 
        SELECT 
          NULL ot
        , NULL seq
        , NULL ob
        , NULL ob1
        , pe.per
        , pe.dtini
        , pe.dtfim
        , NULL obs
        , NULL nivel
        , NULL ref
        , NULL tam
        , NULL cor
        , NULL p_previsto
        , NULL p_real
        FROM period pe
        ORDER BY 
          1 DESC NULLS FIRST
        , 2 
    '''

    debug_cursor_execute(cursor, sql)
    consulta = dictlist_lower(cursor)

    dados_per, dados = dictlist_split(
        consulta, lambda row: row['ot'] is None)

    if dados_per:
        row_per = dados_per[0]
        per = row_per['per']
        dtini = row_per['dtini'].date()
        dtfim = row_per['dtfim'].date()
    else:
        per = None
        dtini = None
        dtfim = None

    oss = set()
    for row in dados:
        row['item'] = item_str(row['nivel'], row['ref'], row['tam'], row['cor'])
        row['op'] = ""
        row['os'] = ""
        if row['obs']:
            obs_list = split_numbers(row['obs'])
            if obs_list:
                row['os'] = obs_list[0]
                oss.add(row['os'])
        else:
            row['obs'] = ""

    if oss:
        data_os = lotes.queries.os.os_inform(cursor, tuple(oss))
    else:
        data_os = []
    dict_os = {
        f"{row['OS']}": row
        for row in data_os
    }
    for row in dados:
        if row['os']:
            if row['os'] in dict_os:
                op = dict_os[row['os']]['OP']
                if op:
                    row['op'] = f"{op}"
                else:
                    row['op'] = ""
            else:
                row['os'] = "Não"

    return dados, per, dtini, dtfim
