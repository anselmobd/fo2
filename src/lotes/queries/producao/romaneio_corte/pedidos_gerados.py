from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.queries.pedido.ped_alter import (
    pedido_matriz_de_pedido_filial,
)
from lotes.queries.pedido.pedido_filial import (
    pedidos_filial_na_data,
)

def query(cursor, data):
    clientes = pedidos_filial_na_data(cursor, data)
    pprint(clientes)

    dados = []
    for cliente in clientes:
        for nf_ped in clientes[cliente]:
            sql = f'''
                select
                  '{cliente}' cliente
                , {nf_ped['ped']} pedido_filial
                , pv.OBSERVACAO obs
                , pvi.CD_IT_PE_NIVEL99 ||'.'|| pvi.CD_IT_PE_GRUPO ||'.'|| pvi.CD_IT_PE_SUBGRUPO  ||'.'|| pvi.CD_IT_PE_ITEM item
                , pvi.QTDE_PEDIDA mov_qtd
                from PEDI_100 pv
                join PEDI_110 pvi
                  on pvi.PEDIDO_VENDA = pv.PEDIDO_VENDA
                where 1=1
                  and pv.PEDIDO_VENDA = {nf_ped['ped']}
                order by
                  pvi.SEQ_ITEM_PEDIDO 
            '''
            debug_cursor_execute(cursor, sql)
            dados_cliente = dictlist_lower(cursor)

            pedido_matriz = pedido_matriz_de_pedido_filial(
                cursor, nf_ped['ped']
            )
            if pedido_matriz:
                ped_matriz = pedido_matriz[0]['pedido_compra']
                ped_matriz_nf = '*' if (
                    pedido_matriz[0]['situacao_pedido'] == 4
                    and pedido_matriz[0]['itens_nf_entrada'] > 0
                ) else ''
            else:
                ped_matriz = '+'
                ped_matriz_nf = ''

            for row in dados_cliente:
                row['pedido_matriz'] = ped_matriz
                row['pedido_matriz_nf'] = ped_matriz_nf
                row['cliente'] = row['cliente'].upper()
                row['mov_qtd'] = round(row['mov_qtd'])
                obs_parts = row['obs'].split(':')
                if len(obs_parts) > 2:
                    row['obs'] = obs_parts[2].strip()
                else:
                    row['obs'] = '-'
                dados.append(row)

    return dados