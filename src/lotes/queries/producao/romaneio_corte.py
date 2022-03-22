from pprint import pprint

from django.utils.text import slugify

from utils.functions.models import rows_to_dict_list_lower
from utils.functions.queries import debug_cursor_execute


def query_completa(
        cursor, data=None, nf=False,
        cliente=None, cliente_slug=None):
    data_value = (
        f"DATE '{data}'"
    ) if data else 'NULL'

    filtra_cliente = f"""--
        AND (
          CASE WHEN op.PEDIDO_VENDA = 0
          THEN 'ESTOQUE' 
          ELSE COALESCE(cli.FANTASIA_CLIENTE, cli.NOME_CLIENTE)
          END
        ) = '{cliente}'
    """ if cliente else ''

    sql = f"""
        WITH
          filtro AS 
        (
          SELECT 
            16 EST
          , {data_value} DT 
          FROM dual 
          WHERE {data_value} IS NOT NULL
        )
        , op_algum_mov AS 
        ( SELECT DISTINCT 
            ml.ORDEM_PRODUCAO OP
          , SUM(COALESCE(ml.QTDE_PRODUZIDA, 0)) MOV_QTD
          FROM filtro, pcpc_045 ml
          WHERE ml.PCPC040_ESTCONF = filtro.EST
            AND ml.DATA_PRODUCAO = filtro.DT
          HAVING
            SUM(COALESCE(ml.QTDE_PRODUZIDA, 0)) > 0
          GROUP BY 
            ml.ORDEM_PRODUCAO
        )
        , op_seq_est_16 AS
        ( SELECT DISTINCT 
            o.OP
          , max(l.SEQUENCIA_ESTAGIO) SEQ_EST
          FROM filtro, PCPC_040 l
          JOIN op_algum_mov o
            ON o.OP = l.ORDEM_PRODUCAO
          WHERE l.CODIGO_ESTAGIO = filtro.EST
          GROUP BY
            o.OP
        )
        , op_completas_ate_16 AS
        ( SELECT
            o.OP
          FROM PCPC_040 l
          JOIN op_seq_est_16 o
            ON o.OP = l.ORDEM_PRODUCAO
          AND o.SEQ_EST >= l.SEQUENCIA_ESTAGIO
          HAVING 
            sum(l.QTDE_PECAS_PROG) = sum(l.QTDE_PECAS_PROD + l.QTDE_PERDAS)
          GROUP BY
            o.OP
        )
        SELECT DISTINCT 
          CASE WHEN op.PEDIDO_VENDA = 0
          THEN 0
          ELSE 1
          END PEDIDO_ORDEM
        , l.ORDEM_PRODUCAO OP
        , l.PROCONF_NIVEL99 nivel
        , l.PROCONF_GRUPO ref
        , l.PROCONF_SUBGRUPO tam
        , t.ORDEM_TAMANHO
        , l.PROCONF_ITEM cor
        , op.PEDIDO_VENDA ped
        , ped.COD_PED_CLIENTE PED_CLI
        , cli.FANTASIA_CLIENTE
        , cli.NOME_CLIENTE
        , CASE WHEN op.PEDIDO_VENDA = 0
          THEN 'ESTOQUE' 
          ELSE COALESCE(cli.FANTASIA_CLIENTE, cli.NOME_CLIENTE)
          END CLIENTE
        , cli.CGC_9
        , cli.CGC_4
        , cli.CGC_2
        , sum(l.QTDE_PECAS_PROD + l.QTDE_PERDAS) mov_qtd
        FROM filtro, PCPC_040 l
        JOIN op_completas_ate_16 oc16
          ON oc16.OP = l.ORDEM_PRODUCAO
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        JOIN pcpc_020 op
          ON op.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        LEFT JOIN PEDI_100 ped
          ON ped.PEDIDO_VENDA = op.PEDIDO_VENDA
        LEFT JOIN PEDI_010 cli
          ON cli.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND cli.CGC_4 = ped.CLI_PED_CGC_CLI4
         AND cli.CGC_2 = ped.CLI_PED_CGC_CLI2
        WHERE filtro.EST = l.CODIGO_ESTAGIO 
          {filtra_cliente} -- filtra_cliente
        GROUP BY 
          l.ORDEM_PRODUCAO
        , l.PROCONF_NIVEL99
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        , op.PEDIDO_VENDA
        , ped.COD_PED_CLIENTE
        , cli.FANTASIA_CLIENTE
        , cli.NOME_CLIENTE
        , cli.CGC_9
        , cli.CGC_4
        , cli.CGC_2
        ORDER BY 
          CASE WHEN op.PEDIDO_VENDA = 0
          THEN 0
          ELSE 1
          END
        , cli.FANTASIA_CLIENTE
        , cli.NOME_CLIENTE
        , cli.CGC_9
        , cli.CGC_4
        , cli.CGC_2
        , ped.COD_PED_CLIENTE
        , op.PEDIDO_VENDA
        , l.ORDEM_PRODUCAO
        , l.PROCONF_NIVEL99
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
    """
    debug_cursor_execute(cursor, sql)
    dados = rows_to_dict_list_lower(cursor)

    if cliente_slug:
        dados = [
            row
            for row in dados
            if slugify(row['cliente']) == cliente_slug
        ]

    clientes = {}
    for row in dados:
        if not row['ped']:
            row['ped'] = '-'
        if not row['ped_cli']:
            row['ped_cli'] = '-'
        if nf:
            if row['cliente'] not in clientes:
                clientes[row['cliente']] = {}
            cliaux = clientes[row['cliente']]
            if row['ped_cli'] not in cliaux:
                cliaux[row['ped_cli']] = set()
            pedaux = cliaux[row['ped_cli']]
            pedaux.add(row['op'])
        row['item'] = '.'.join([
            row['nivel'],
            row['ref'],
            row['tam'],
            row['cor'],
        ])

    if nf:
        for cli in clientes:
            cliaux = clientes[cli]
            if cli == 'ESTOQUE':
                ops = ', '.join(map(str, cliaux['-']))
                cliaux['obs'] = f"OP({ops})"
            else:
                peds = list(cliaux.keys())
                cliaux['obs'] = ''
                sep = ''
                for ped in peds:
                    ops = ', '.join(map(str, cliaux[ped]))
                    cliaux['obs'] += sep + f"Pedido({ped})-OP({ops})"
                    sep = ', '
        for row in dados:
            row['obs'] = clientes[row['cliente']]['obs']
        
        dados = dados, list(clientes.keys())

    return dados


def query_OLD(cursor, data=None):
    filtro_data = (
        f"AND ml.DATA_PRODUCAO = '{data}'"
    ) if data else ''

    sql = f'''
        WITH mlseq AS
        (
        SELECT 
          ml.PCPC040_PERCONF per
        , ml.PCPC040_ORDCONF ord
        , ml.PCPC040_ESTCONF est
        , max(ml.SEQUENCIA) seq
        FROM  PCPC_045 ml
        GROUP BY
          ml.PCPC040_PERCONF
        , ml.PCPC040_ORDCONF
        , ml.PCPC040_ESTCONF
        ) 
        SELECT
          TO_DATE(ml.DATA_PRODUCAO) data
        , l.ORDEM_PRODUCAO op
        , l.PROCONF_GRUPO ref
        , l.PROCONF_SUBGRUPO tam
        , l.PROCONF_ITEM cor
        , count(l.ORDEM_CONFECCAO) lotes
        , sum(l.QTDE_PECAS_PROD) qtd
        , sum(l.QTDE_PERDAS) perda
        FROM PCPC_040 l
        JOIN mlseq mls
          ON mls.per = l.PERIODO_PRODUCAO
         AND mls.ord = l.ORDEM_CONFECCAO
         AND mls.est = l.CODIGO_ESTAGIO
        JOIN PCPC_045 ml
          ON ml.PCPC040_PERCONF = l.PERIODO_PRODUCAO
         AND ml.PCPC040_ORDCONF = l.ORDEM_CONFECCAO 
         AND ml.PCPC040_ESTCONF = l.CODIGO_ESTAGIO
         AND ml.SEQUENCIA = mls.seq
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
          -- AND ml.DATA_PRODUCAO = DATE '2022-02-15'
          {filtro_data} -- filtro_data
          AND l.CODIGO_ESTAGIO = 16
          AND l.QTDE_PECAS_PROD <> 0 
        GROUP BY 
          ml.DATA_PRODUCAO
        , l.ORDEM_PRODUCAO
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        ORDER BY 
          ml.DATA_PRODUCAO
        , l.ORDEM_PRODUCAO
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
    '''
    debug_cursor_execute(cursor, sql)
    dados = rows_to_dict_list_lower(cursor)
    for row in dados:
        row['data'] = row['data'].date()
    return dados


def query(cursor, data=None):
    data_value = (
        f"DATE '{data}'"
    ) if data else 'NULL'

    sql = f'''
        WITH
          filtro AS 
        (
          SELECT 
            16 EST
          , {data_value} DT 
          FROM dual 
          WHERE {data_value} IS NOT NULL
        )
        , op_mov AS 
        ( SELECT  
            ml.ORDEM_PRODUCAO OP
          , ml.PCPC040_PERCONF PER
          , ml.PCPC040_ORDCONF OC
          , SUM(COALESCE(ml.QTDE_PRODUZIDA, 0)) MOV_QTD
          FROM filtro, pcpc_045 ml
          WHERE 1=1
          --  AND ml.ORDEM_PRODUCAO = 33998
            AND ml.PCPC040_ESTCONF = filtro.EST
            AND ml.DATA_PRODUCAO = filtro.DT
          HAVING
            SUM(COALESCE(ml.QTDE_PRODUZIDA, 0)) > 0
          GROUP BY 
            ml.ORDEM_PRODUCAO
          , ml.PCPC040_PERCONF
          , ml.PCPC040_ORDCONF
        )
        , op_min_prep AS 
        ( SELECT
            l.ORDEM_PRODUCAO OP
          , min(l.PERIODO_PRODUCAO) PER1
          , min(l.SEQUENCIA_ESTAGIO) SEQ1
          FROM PCPC_040 l
          GROUP BY 
            l.ORDEM_PRODUCAO
        )
        , op_min AS 
        ( SELECT
            om.OP
          , om.PER1
          , om.SEQ1
          , min(l.ORDEM_CONFECCAO) OC1
          , min(
              CASE WHEN l.SEQUENCIA_ESTAGIO = om.SEQ1
              THEN l.CODIGO_ESTAGIO
              ELSE 999
              END 
            ) EST1
          FROM op_min_prep om
          JOIN PCPC_040 l
            ON l.ORDEM_PRODUCAO = om.OP
           AND l.PERIODO_PRODUCAO = om.PER1
          GROUP BY 
            om.OP
          , om.PER1
          , om.SEQ1
        )
        , op_lotes AS 
        ( SELECT
            mov.*
          , l.QTDE_PECAS_PROG LOTE_QTD
          , mov.MOV_QTD / l.QTDE_PECAS_PROG MOV_LOTES
          , l.PROCONF_NIVEL99 NIVEL
          , l.PROCONF_GRUPO REF
          , t.ORDEM_TAMANHO TAM_ORD
          , l.PROCONF_SUBGRUPO TAM
          , l.PROCONF_ITEM COR
          FROM op_mov mov
          JOIN op_min om
            ON om.OP = mov.OP
          JOIN pcpc_040 l
            ON l.PERIODO_PRODUCAO = mov.PER
           AND l.ORDEM_CONFECCAO = mov.OC
           AND l.CODIGO_ESTAGIO = om.EST1
          LEFT JOIN BASI_220 t -- tamanhos
            ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        )
        , op_ref AS 
        ( SELECT
            ol.OP
          , ol.NIVEL  
          , ol.REF  
          , ol.TAM_ORD  
          , ol.TAM  
          , ol.COR  
          , sum(ol.MOV_QTD) MOV_QTD
          , sum(ol.MOV_LOTES) MOV_LOTES
          FROM op_lotes ol
          GROUP BY 
            ol.OP
          , ol.NIVEL  
          , ol.REF  
          , ol.TAM_ORD  
          , ol.TAM  
          , ol.COR  
          ORDER BY 
            ol.OP
          , ol.REF  
          , ol.COR  
          , ol.TAM_ORD  
        )
        SELECT 
          CASE WHEN op.PEDIDO_VENDA = 0
          THEN 0
          ELSE 1
          END PEDIDO_ORDEM
        , CASE WHEN op.PEDIDO_VENDA = 0
          THEN 'ESTOQUE' 
          ELSE COALESCE(cli.FANTASIA_CLIENTE, cli.NOME_CLIENTE)
          END CLIENTE
        , ped.COD_PED_CLIENTE PED_CLI
        , ped.PEDIDO_VENDA PED
        , ol.OP
        , ol.NIVEL
        , ol.REF
        , ol.TAM_ORD
        , ol.TAM
        , ol.COR
        , ol.MOV_QTD
        , ol.MOV_LOTES
        FROM op_ref ol
        JOIN pcpc_020 op
          ON op.ORDEM_PRODUCAO = ol.OP
        LEFT JOIN PEDI_100 ped
          ON ped.PEDIDO_VENDA = op.PEDIDO_VENDA
        LEFT JOIN PEDI_010 cli
          ON cli.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND cli.CGC_4 = ped.CLI_PED_CGC_CLI4
         AND cli.CGC_2 = ped.CLI_PED_CGC_CLI2
        ORDER BY
          1
        , 2
        , ol.OP
        , ol.REF
        , ol.COR
        , ol.TAM_ORD
    '''
    debug_cursor_execute(cursor, sql)
    dados = rows_to_dict_list_lower(cursor)

    if not dados:
        return

    ops = set()
    for row in dados:
        ops.add(row['op'])

    str_ops = ', '.join([
        str(op) for op in list(ops)
    ])

    sql = f'''
        WITH
          op_min_prep AS 
        ( SELECT
            l.ORDEM_PRODUCAO OP
          , min(l.PERIODO_PRODUCAO) PER1
          , min(l.SEQUENCIA_ESTAGIO) SEQ1
          FROM PCPC_040 l
          GROUP BY 
            l.ORDEM_PRODUCAO
        )
        , op_min AS 
        ( SELECT
            om.OP
          , om.PER1
          , om.SEQ1
          , min(l.ORDEM_CONFECCAO) OC1
          , min(
              CASE WHEN l.SEQUENCIA_ESTAGIO = om.SEQ1
              THEN l.CODIGO_ESTAGIO
              ELSE 999
              END 
            ) EST1
          FROM op_min_prep om
          JOIN PCPC_040 l
            ON l.ORDEM_PRODUCAO = om.OP
           AND l.PERIODO_PRODUCAO = om.PER1
          GROUP BY 
            om.OP
          , om.PER1
          , om.SEQ1
        )
        SELECT 
          l.ORDEM_PRODUCAO OP
        , l.PROCONF_NIVEL99 NIVEL
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , sum(l.QTDE_PECAS_PROG) TOT_QTD
        , COUNT(DISTINCT COALESCE(l.PERIODO_PRODUCAO || l.ORDEM_CONFECCAO, '')) TOT_LOTES
        FROM op_min om
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = om.OP
         AND l.CODIGO_ESTAGIO = om.EST1 
        WHERE om.OP IN
          ({str_ops})
        GROUP BY 
          l.ORDEM_PRODUCAO
        , l.PROCONF_NIVEL99
        , l.PROCONF_GRUPO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
    '''
    debug_cursor_execute(cursor, sql)
    dados_op_tot = rows_to_dict_list_lower(cursor)

    for row in dados_op_tot:
        row['item'] = '.'.join([
            row['nivel'],
            row['ref'],
            row['tam'],
            row['cor'],
        ])

    op_tot = {
        (r['op'], r['item']):
            (
                r['tot_qtd'],
                r['tot_lotes'],
            )
        for r in dados_op_tot
    }

    for row in dados:
        if not row['ped']:
            row['ped'] = '-'
        if not row['ped_cli']:
            row['ped_cli'] = '-'
        row['item'] = '.'.join([
            row['nivel'],
            row['ref'],
            row['tam'],
            row['cor'],
        ])
        row['tot_qtd'], row['tot_lotes'] = op_tot[(row['op'], row['item'])]
        row['percent_qtd'] = f"{round(row['mov_qtd']/row['tot_qtd']*100)}%"
        row['percent_lotes'] = f"{round(row['mov_lotes']/row['tot_lotes']*100)}%"

    return dados
