from pprint import pprint

from django.utils.text import slugify

from utils.functions.models import rows_to_dict_list_lower
from utils.functions.queries import debug_cursor_execute

from lotes.queries.pedido.ped_alter import (
    query_pedidos_filial,
    pedido_matriz_de_pedido_filial,
)


def query(cursor, data=None, para_nf=False, cliente_slug=None):
    data_value = (
        f"DATE '{data}'"
    ) if data else 'NULL'

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
        row['cliente_slug'] = slugify(row['cliente'])

    if cliente_slug:
        dados = [
            row
            for row in dados
            if row['cliente_slug'] == cliente_slug
        ]

    if para_nf:
        clientes = {}
        for row in dados:
            if row['cliente_slug'] not in clientes:
                clientes[row['cliente_slug']] = {
                    'cliente': row['cliente'],
                    'pedidos': {}
                }
            cliaux = clientes[row['cliente_slug']]['pedidos']
            if row['ped_cli'] not in cliaux:
                cliaux[row['ped_cli']] = {row['op']}
            else:
                cliaux[row['ped_cli']].add(row['op'])

        peds = query_pedidos_filial(cursor, data)

        for cli in clientes:
            cliaux = clientes[cli]
            if cli == 'estoque':
                ops = ', '.join(map(str, cliaux['pedidos']['-']))
                cliaux['obs'] = f"OP({ops})"
            else:
                cliaux['obs'] = ''
                sep = ''
                for ped in cliaux['pedidos']:
                    ops = ', '.join(map(str, cliaux['pedidos'][ped]))
                    cliaux['obs'] += sep + f"Pedido({ped})-OP({ops})"
                    sep = ', '

            if cli in peds:
                ped1 = peds[cli][0]
                cliaux['pedido_filial'] = ped1['ped']
                cliaux['pedido_filial_nf'] = '*' if ped1['nf'] else ''
                cliaux['pedido_filial_quant'] = '+' if len(peds[cli]) > 1 else ''
                pedido_matriz = pedido_matriz_de_pedido_filial(
                    cursor, ped1['ped']
                )
                if pedido_matriz:
                    cliaux['pedido_matriz'] = pedido_matriz[0]['pedido_compra']
                else:
                    cliaux['pedido_matriz'] = '-'
            else:
                cliaux['pedido_filial'] = '-'
                cliaux['pedido_matriz'] = '-'

        for row in dados:
            cli_slug = row['cliente_slug']
            cli_row = clientes[cli_slug]
            row['obs'] = cli_row['obs']
            row['pedido_filial'] = cli_row['pedido_filial']
            row['pedido_filial_nf'] = cli_row.get('pedido_filial_nf', '')
            row['pedido_filial_quant'] = cli_row.get('pedido_filial_quant', '')
            row['pedido_matriz'] = cli_row['pedido_matriz']
        
        dados = dados, clientes

    return dados
