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


def pedidos_filial_na_data(cursor, data=None):
    filtra_data = f"""--
        AND p.DATA_EMIS_VENDA = DATE '{data}'
        AND p.DATA_ENTR_VENDA = DATE '{data}'
    """ if data else ''
    sql = f"""
        SELECT
          p.PEDIDO_VENDA ped
        , p.OBSERVACAO obs
        , p.DATA_EMIS_VENDA data
        , f.NUM_NOTA_FISCAL nf
        FROM PEDI_100 p
        LEFT JOIN FATU_050 f
          ON f.PEDIDO_VENDA = p.PEDIDO_VENDA
        WHERE 1=1
          AND p.CODIGO_EMPRESA = 3
          AND p.COD_CANCELAMENTO = 0
          {filtra_data} -- filtra_data
    """
    debug_cursor_execute(cursor, sql)
    dados = rows_to_dict_list_lower(cursor)

    peds = {}
    for row in dados:
        # obs = row.pop('obs')
        obs = row['obs']
        if not obs:
            continue
        if not re.search('^\[MPCFM\] ', obs):
            continue
        if data and not re.search(f"Data: {data}", obs):
            continue
        if re.search("Producao para estoque:", obs):
            cliente = 'estoque'
        else:
            cliente_match = re.search('Producao para o cliente ([^ ]+):', obs)
            if not cliente_match:
                continue
            cliente = cliente_match.group(1).lower()
        if cliente not in peds:
            peds[cliente] = []
        peds[cliente].append(row)
    return peds


def pedido_matriz_de_pedido_filial(cursor, pedido_filial):
    sql = f"""
        SELECT 
          pcc.*
        , (
            SELECT
              count(*)
            FROM OBRF_015 nfei
            WHERE nfei.PEDIDO_COMPRA = pcc.PEDIDO_COMPRA
          ) itens_nf_entrada
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
          AND pcc.OBSERVACAO LIKE '[PED.FILIAL:%'
          AND pcc.OBSERVACAO = '[PED.FILIAL:' || pvc.PEDIDO_VENDA || ']'
          --
          AND pcc.COD_CANCELAMENTO = 0
    """
    debug_cursor_execute(cursor, sql)
    return rows_to_dict_list_lower(cursor)


def inclui_pedido_compra_matriz_capa(cursor, pedido_filial):
    sql = f"""
        INSERT INTO SYSTEXTIL.SUPR_090
        ( PEDIDO_COMPRA, DT_EMIS_PED_COMP, COND_PGTO_COMPRA,
          FORN_PED_FORNE9, FORN_PED_FORNE4, FORN_PED_FORNE2, DATA_PREV_ENTR,
          TRAN_PED_FORNE9, TRAN_PED_FORNE4, TRAN_PED_FORNE2, TIPO_FRETE,
          COD_END_ENTREGA, COD_END_COBRANCA, CODIGO_COMPRADOR, VENDEDOR_CONTATO,
          COD_CANCELAMENTO, SITUACAO_PEDIDO, VALOR_FRETE, VALOR_OUTRAS, COD_PORTADOR,
          CODIGO_EMPRESA, VAL_ENC_FINAN, TAB_PRECO, CODIGO_TRANSACAO, FLAG_EXPORTADO,
          COD_MOEDA, DATETIME_PEDIDO, TIME_PEDIDO, PESO_TOTAL, EXECUTA_TRIGGER,
          OBSERVACAO, DATA_CHEGADA, VOLUME, TIPO_FRETE_REDESPACHO, NUMERO_COMPRA_OBC,
          E_MAIL, ASSUNTO_EMAIL, TEXTO_EMAIL, TIPO_PEDIDO, ENVIA_EMAIL_EMERGENCIAL,
          PEDIDO_REGISTRO, REUTILIZA_SDCV_OBC, ORDEM_SERVICO
        )
        SELECT 
          ( SELECT 
              COALESCE(max(pcc.PEDIDO_COMPRA), 702000) + 1
            FROM SUPR_090 pcc
            WHERE 1=1
              AND pcc.PEDIDO_COMPRA > 702000
          ) -- PEDIDO_COMPRA
        , pvc.DATA_EMIS_VENDA -- DT_EMIS_PED_COMP
        , 1 -- COND_PGTO_COMPRA
        , 7681643 -- FORN_PED_FORNE9
        , 2 -- FORN_PED_FORNE4
        , 78 -- FORN_PED_FORNE2
        , pvc.DATA_EMIS_VENDA -- DATA_PREV_ENTR
        , 0 -- TRAN_PED_FORNE9
        , 0 -- TRAN_PED_FORNE4
        , 0 -- TRAN_PED_FORNE2
        , 9 -- TIPO_FRETE
        , 1 -- COD_END_ENTREGA
        , 1 -- COD_END_COBRANCA
        , 1 -- CODIGO_COMPRADOR
        , '[PED.FILIAL:' || pvc.PEDIDO_VENDA || ']' -- VENDEDOR_CONTATO
        , 0 -- COD_CANCELAMENTO
        , 1 -- SITUACAO_PEDIDO a emitir
        , 0 -- VALOR_FRETE
        , 0 -- VALOR_OUTRAS
        , 0 -- COD_PORTADOR
        , 1 -- CODIGO_EMPRESA
        , 0 -- VAL_ENC_FINAN
        , 0 -- TAB_PRECO
        , 0 -- CODIGO_TRANSACAO
        , 0 -- FLAG_EXPORTADO
        , 0 -- COD_MOEDA
        , pvc.DATA_EMIS_VENDA -- DATETIME_PEDIDO
        , TIMESTAMP '1970-01-01 00:00:00.000000' -- TIME_PEDIDO
        , 0 -- PESO_TOTAL
        , NULL -- EXECUTA_TRIGGER
        , '[PED.FILIAL:' || pvc.PEDIDO_VENDA || ']' -- OBSERVACAO
        , NULL -- DATA_CHEGADA
        , 0 -- VOLUME
        , 4 -- TIPO_FRETE_REDESPACHO
        , NULL -- NUMERO_COMPRA_OBC
        , NULL -- E_MAIL
        , NULL -- ASSUNTO_EMAIL
        , NULL -- TEXTO_EMAIL
        , 0 -- TIPO_PEDIDO
        , 0 -- ENVIA_EMAIL_EMERGENCIAL
        , NULL -- PEDIDO_REGISTRO
        , NULL -- REUTILIZA_SDCV_OBC
        , 0 -- ORDEM_SERVICO
        FROM PEDI_100 pvc -- capa de pedido de compra
        WHERE 1=1
          AND pvc.PEDIDO_VENDA = {pedido_filial}
    """
    cursor.execute(sql)

def emite_pedido_compra_matriz(cursor, pedido_compra, emite=True):
    val_situacao = '2' if emite else '1'
    sql = f"""
        UPDATE SUPR_090
        SET SITUACAO_PEDIDO = {val_situacao}
        WHERE PEDIDO_COMPRA = {pedido_compra}
    """
    cursor.execute(sql)

def exclui_pedido_compra_matriz_capa(cursor, pedido_compra):
    sql = f"""
        DELETE FROM SYSTEXTIL.SUPR_090
        WHERE PEDIDO_COMPRA = {pedido_compra}
    """
    cursor.execute(sql)


def inclui_pedido_compra_matriz_itens(cursor, pedido_filial, pedido_compra):
    sql = f"""
        INSERT INTO SYSTEXTIL.SUPR_100
        ( NUM_PED_COMPRA, SEQ_ITEM_PEDIDO, ITEM_100_NIVEL99, ITEM_100_GRUPO,
          ITEM_100_SUBGRUPO, ITEM_100_ITEM, DESCRICAO_ITEM, UNIDADE_MEDIDA,
          QTDE_PEDIDA_ITEM, QTDE_SALDO_ITEM, PRECO_ITEM_COMP, PERCENTUAL_DESC, 
          PERCENTUAL_IPI, OUTRAS_DESPESAS, CENTRO_CUSTO, CODIGO_DEPOSITO, 
          DATA_PREV_ENTR, NUM_REQUISICAO, SEQ_ITEM_REQ, COD_CANCELAMENTO, 
          DT_CANCELAMENTO, SITUACAO_ITEM, NUMERO_COLETA, CODIGO_CONTABIL, 
          PERC_ENC_FINAN, DATA_PREV_ENTR_INI, FLAG_ORCAMENTO, PROJETO, SUBPROJETO, 
          SERVICO, PERC_IVA, PERIODO_COMPRAS, OBSERVACAO_ITEM, EXECUTA_TRIGGER, 
          UNIDADE_CONV, FATOR_CONV, VALOR_CONV, COD_FABRICANTE_PROD, COD_PROD_FABRICANTE, 
          NUMERO_REQ_OBC, CNPJ9_DESTINO, CNPJ4_DESTINO, CNPJ2_DESTINO, COD_APLICACAO, 
          ORIGEM_ITEM, NUMERO_COTACAO, QTDE_A_ENTREGAR, FLAG_MARCAR, CHAVE_NF, 
          SEQUENCIA_ITEM_NF, REUTILIZA_SDCV_OBC, CODIGO_TRANSACAO
        )
        SELECT
          {pedido_compra} -- NUM_PED_COMPRA
        , pvi.SEQ_ITEM_PEDIDO -- SEQ_ITEM_PEDIDO
        , pvi.CD_IT_PE_NIVEL99 -- ITEM_100_NIVEL99
        , pvi.CD_IT_PE_GRUPO -- ITEM_100_GRUPO
        , pvi.CD_IT_PE_SUBGRUPO -- ITEM_100_SUBGRUPO
        , pvi.CD_IT_PE_ITEM -- ITEM_100_ITEM
        , i.NARRATIVA -- DESCRICAO_ITEM
        , 'UN' -- UNIDADE_MEDIDA
        , pvi.QTDE_PEDIDA -- QTDE_PEDIDA_ITEM
        , pvi.QTDE_PEDIDA -- QTDE_SALDO_ITEM
        , 2 -- PRECO_ITEM_COMP
        , 0 -- PERCENTUAL_DESC
        , 0 -- PERCENTUAL_IPI
        , 0 -- OUTRAS_DESPESAS
        , 431013 -- CENTRO_CUSTO -- CORTE
        , 231 -- CODIGO_DEPOSITO
        , pvc.DATA_EMIS_VENDA -- DATA_PREV_ENTR
        , 0 -- NUM_REQUISICAO
        , 0 -- SEQ_ITEM_REQ
        , 0 -- COD_CANCELAMENTO
        , NULL -- DT_CANCELAMENTO
        , 1 -- SITUACAO_ITEM
        , 0 -- NUMERO_COLETA
        , 128 -- CODIGO_CONTABIL -- semi-acabado MD
        , 0 -- PERC_ENC_FINAN
        , pvc.DATA_EMIS_VENDA -- DATA_PREV_ENTR_INI
        , 0 -- FLAG_ORCAMENTO
        , 0 -- PROJETO
        , 0 -- SUBPROJETO
        , 0 -- SERVICO
        , 0 -- PERC_IVA
        , pvc.NUM_PERIODO_PROD -- PERIODO_COMPRAS
        , NULL -- OBSERVACAO_ITEM
        , NULL -- EXECUTA_TRIGGER
        , NULL -- UNIDADE_CONV
        , 0 -- FATOR_CONV
        , 2 -- VALOR_CONV
        , ' ' -- COD_FABRICANTE_PROD
        , ' ' -- COD_PROD_FABRICANTE
        , NULL -- NUMERO_REQ_OBC
        , 0 -- CNPJ9_DESTINO
        , 0 -- CNPJ4_DESTINO
        , 0 -- CNPJ2_DESTINO
        , 0 -- COD_APLICACAO
        , 0 -- ORIGEM_ITEM
        , NULL -- NUMERO_COTACAO
        , NULL -- QTDE_A_ENTREGAR
        , NULL -- FLAG_MARCAR
        , NULL -- CHAVE_NF
        , NULL -- SEQUENCIA_ITEM_NF
        , NULL -- REUTILIZA_SDCV_OBC
        , 0 -- CODIGO_TRANSACAO
        FROM PEDI_100 pvc -- capa de pedido de compra
        JOIN PEDI_110 pvi -- item de pedido de compra
          ON pvi.PEDIDO_VENDA = pvc.PEDIDO_VENDA
        LEFT JOIN basi_010 i -- item 
          ON i.NIVEL_ESTRUTURA = pvi.CD_IT_PE_NIVEL99
         AND i.GRUPO_ESTRUTURA = pvi.CD_IT_PE_GRUPO
         AND i.SUBGRU_ESTRUTURA = pvi.CD_IT_PE_SUBGRUPO
         AND i.ITEM_ESTRUTURA = pvi.CD_IT_PE_ITEM
        WHERE 1=1
          AND pvc.PEDIDO_VENDA = {pedido_filial}
    """
    cursor.execute(sql)


def exclui_pedido_compra_matriz_itens(cursor, pedido_compra):
    sql = f"""
        DELETE FROM SUPR_100
        WHERE NUM_PED_COMPRA = {pedido_compra}
    """
    cursor.execute(sql)


def get_pedido_compra_matriz_itens(cursor, pedido_compra):
    sql = f"""
        SELECT
          *
        FROM SUPR_100
        WHERE NUM_PED_COMPRA = {pedido_compra}
    """
    debug_cursor_execute(cursor, sql)
    return rows_to_dict_list_lower(cursor)
