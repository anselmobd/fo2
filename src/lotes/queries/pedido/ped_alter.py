import re
from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower
from utils.functions.queries import debug_cursor_execute

__all__=['altera_pedido', 'altera_pedido_itens']


def altera_pedido(cursor, data, pedido, empresa, qtd, observacao):
    sql = f"""
        UPDATE PEDI_100 p 
        SET 
          p.OBSERVACAO = '{observacao}'
        , p.COD_PED_CLIENTE = ''
        , p.DATA_EMIS_VENDA = DATE '{data}'
        , p.DATA_ENTR_VENDA = DATE '{data}'
        , p.DATA_DIGIT_VENDA = CURRENT_DATE
        , p.NUM_PERIODO_PROD = (
            SELECT 
              p.PERIODO_PRODUCAO
            FROM PCPC_010 p -- períodos
            WHERE 1=1
              AND p.AREA_PERIODO = 1
              AND p.DATA_INI_PERIODO <= DATE '{data}'
              AND p.DATA_FIM_PERIODO >= DATE '{data}'
          )
        , QTDE_TOTAL_PEDI={qtd}
        , VALOR_TOTAL_PEDI={qtd*2}
        , QTDE_SALDO_PEDI={qtd}
        , VALOR_SALDO_PEDI={qtd*2}
        , VALOR_LIQ_ITENS={qtd*2}
        WHERE 1=1
          AND p.CODIGO_EMPRESA = {empresa}
          AND p.PEDIDO_VENDA = {pedido}
    """
    cursor.execute(sql)


def altera_pedido_itens(cursor, pedido, nat_cod, nat_uf, dados):
    exclui_pedido_itens(cursor, pedido)
    for idx, row in enumerate(dados):
        inclui_pedido_item(cursor, pedido, nat_cod, nat_uf, idx+1, row)


def exclui_pedido_itens(cursor, pedido):
    sql = f"""
        DELETE FROM SYSTEXTIL.PEDI_110
        WHERE PEDIDO_VENDA = {pedido}
    """
    cursor.execute(sql)

def inclui_pedido_item(cursor, pedido, nat_cod, nat_uf, seq, row):
    row['pedido'] = pedido
    row['seq'] = seq
    row['nat_cod'] = nat_cod
    row['nat_uf'] = nat_uf
    sql = """
        INSERT INTO SYSTEXTIL.PEDI_110
        (PEDIDO_VENDA, SEQ_ITEM_PEDIDO, CD_IT_PE_NIVEL99, CD_IT_PE_GRUPO, CD_IT_PE_SUBGRUPO, CD_IT_PE_ITEM, CODIGO_DEPOSITO, LOTE_EMPENHADO, QTDE_DISTRIBUIDA, QTDE_PEDIDA, VALOR_UNITARIO, PERCENTUAL_DESC, QTDE_FATURADA, NR_SOLICITACAO, QTDE_AFATURAR, SITUACAO_FATU_IT, COD_CANCELAMENTO, DT_CANCELAMENTO, DT_INCLUSAO, QTDE_ROLOS, NR_PEDIDO_SUB, SEQ_ITEM_SUB, DEPOSITO_SUB, LOTE_SUB, SEQ_PRINCIPAL, QTDE_PEDIDA_LOJA, QTDE_SUGERIDA, OBSERVACAO1, OBSERVACAO2, CAIXA_PED_OB, KANBAN_PED_OB, MONTADOR_PED_OB, AREA_PED_OB, DATA_ENT_PROG, CAIXA_PEDI_OB, KANBAN_PEDI_OB, CODIGO_ACOMP, DATA_EMPENHO, DATA_SOLICITACAO, ACRESCIMO, ITEM_ATIVO, EXPEDIDOR, DATA_LEITURA_COLETOR, JA_ATUALIZADO, EMPENHO_AUTOMATICO, CORREDOR, BOX, DATA_SUGESTAO, PERC_MAO_OBRA, CARACT, CARACT_ING, CARACT_ESP, NR_SUGESTAO, AGRUPADOR_PRODUCAO, COD_NAT_OP, EST_NAT_OP, CODIGO_EMBALAGEM, UM_FATURAMENTO_UM, UM_FATURAMENTO_QTDE, UM_FATURAMENTO_VALOR, LARGURA, GRAMATURA, NUMERO_RESERVA, EXECUTA_TRIGGER, COD_PED_CLIENTE, SEQ_ORIGINAL, QTDE_VOLUMES, NR_ALTERNATIVA, NR_ROTEIRO, COR_FORMULARIO_FAL, TIPO_SERVICO, GRUPO_MAQUINA, SUBGRUPO_MAQUINA, NUMERO_MAQUINA, MOTIVO_REPROCESSO, DESTINO_PROJETO, PRODUTO_INTEGRACAO, PROD_GRADE_INTEGRACAO, QTDE_PECAS_ATEND, SEQ_ITEM_RESERVA, SEQ_PED_COMPRA, LIQUIDA_SALDO_APROGRAMAR, PERMITE_ATU_WMS, GRADE_ITEM, MODULAR, FLAGETIQPRECO, SEQ_PED_SERVICO, CGC9CLI, CGC4CLI, CGC2CLI, QTDE_ORIGINAL, GRU_ORIGINAL_TROCAX, ITE_ORIGINAL_TROCAX, MOTIVO_TROCA, NIV_ORIGINAL_TROCAX, SUB_ORIGINAL_TROCAX, VALOR_UNITARIO_INSUMO, QTDE_ORIGINAL_PEDIDA, STATUS_EXPEDICAO, CENTRO_CUSTO)
        VALUES({pedido}, {seq}, '{nivel}', '{ref}', '{tam}', '{cor}', 600, 0, 0, {mov_qtd}, 2, 0, 0, 0, 0, 0, 0, NULL, NULL, 0, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, 0, 0, 0, NULL, 0, 0, 0, 0, NULL, 0, NULL, NULL, NULL, 0, 0,
        {nat_cod}, '{nat_uf}', 0, NULL, 0, 0, 0, 0, 0, NULL, NULL, 0, 0, 0, 0, NULL, 0, NULL, NULL, 0, NULL, '00', NULL, NULL, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, 0, 0, 0, 0)
    """.format(**row)
    cursor.execute(sql)


def query_pedidos_filial(cursor, data):
    sql = f"""
        SELECT
          p.PEDIDO_VENDA ped
        , p.OBSERVACAO obs
        FROM PEDI_100 p 
        WHERE 1=1
          AND p.CODIGO_EMPRESA = 3
          AND p.COD_CANCELAMENTO = 0
          AND p.DATA_EMIS_VENDA = DATE '{data}'
          AND p.DATA_ENTR_VENDA = DATE '{data}'
    """
    debug_cursor_execute(cursor, sql)
    dados = rows_to_dict_list_lower(cursor)

    peds = {}
    for row in dados:
        if not row['obs']:
            continue
        if not re.search('^\[MPCFM\] ', row['obs']):
            continue
        if not re.search(f"Data: {data}", row['obs']):
            continue
        if re.search("Producao para estoque:", row['obs']):
            cliente = 'estoque'
        else:
            cliente_match = re.search('Producao para o cliente ([^ ]+):', row['obs'])
            if not cliente_match:
                continue
            cliente = cliente_match.group(1).lower()
        if cliente in peds:
            peds[cliente] = ', '.join([peds[cliente], row['ped']])
        else:
            peds[cliente] = row['ped']
    pprint(peds)
    return peds


def pedido_matriz_de_pedido_filial(cursor, pedido_filial):
    sql = f"""
        SELECT 
          pcc.*
        FROM SUPR_090 pcc, PEDI_100 pvc
        WHERE 1=1
          AND pvc.PEDIDO_VENDA = {pedido_filial}
          AND pcc.FORN_PED_FORNE9 = 7681643 
          AND pcc.FORN_PED_FORNE4 = 2 
          AND pcc.FORN_PED_FORNE2 = 78 
          AND pcc.DT_EMIS_PED_COMP = pvc.DATA_EMIS_VENDA 
          AND pcc.DATA_PREV_ENTR = pvc.DATA_EMIS_VENDA 
          AND pcc.DATETIME_PEDIDO = pvc.DATA_EMIS_VENDA 
          AND pcc.TIME_PEDIDO = TIMESTAMP '1970-01-01 00:00:00.000000'
          AND pcc.VENDEDOR_CONTATO LIKE '[PED.FILIAL:%'
          AND pcc.VENDEDOR_CONTATO = '[PED.FILIAL:' || pvc.PEDIDO_VENDA || ']'
    """
    debug_cursor_execute(cursor, sql)
    dados = rows_to_dict_list_lower(cursor)
