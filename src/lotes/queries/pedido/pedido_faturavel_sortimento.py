from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def pedido_faturavel_sortimento(cursor, deposito, data_de, data_ate):

    filtro_deposito = ''
    if deposito is not None and data_de != '':
        filtro_deposito = f''' --
            AND i.CODIGO_DEPOSITO = {deposito} '''

    filtro_data_de = ''
    if data_de is not None and data_de != '':
        filtro_data_de = ''' --
            AND ped.DATA_ENTR_VENDA >= '{}' '''.format(data_de)

    filtro_data_ate = ''
    if data_ate is not None and data_ate != '':
        filtro_data_ate = ''' --
            AND ped.DATA_ENTR_VENDA <= '{}' '''.format(data_ate)

    sql = f"""
        WITH ped_data_entr AS -- pedidos pré-filtrados
        (
          SELECT
            ped.PEDIDO_VENDA
          FROM PEDI_100 ped -- pedido de venda
          WHERE ped.STATUS_PEDIDO <> 5 -- 5=cancelado
            {filtro_data_de} -- filtro_data_de
            {filtro_data_ate} -- filtro_data_ate
            -- filtro_embarque_de
            -- AND ped.DATA_ENTR_VENDA >= TO_DATE('2019-02-25','YYYY-MM-DD')
            -- filtro_embarque_ate
            -- AND ped.DATA_ENTR_VENDA <= TO_DATE('2020-03-29','YYYY-MM-DD')
          GROUP BY
            ped.PEDIDO_VENDA
        )
        , ped_faturas AS -- pedidos e suas faturas
        (
          SELECT
            ped.PEDIDO_VENDA PEDIDO
          , fok.NUM_NOTA_FISCAL NFOK
          , fe.DOCUMENTO NFDEV
          FROM ped_data_entr ped -- pedido de venda filtrado
          LEFT JOIN FATU_050 fok -- fatura
            ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
           AND fok.SITUACAO_NFISC = 1  -- 1=emitida; 2=cancelada
          LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
            ON fe.NOTA_DEV = fok.NUM_NOTA_FISCAL
           AND fe.SITUACAO_ENTRADA = 1 -- 1=ativa
        )
        , it_ped_qtd AS -- itens de pedidos com qtd
        (
          SELECT
            pf.PEDIDO
          , pf.NFOK
          , pf.NFDEV
          , i.CD_IT_PE_GRUPO REF
          , i.CD_IT_PE_SUBGRUPO TAM
          , i.CD_IT_PE_ITEM COR
          , sum(i.QTDE_PEDIDA) QTD
          FROM ped_faturas pf -- pedidos e suas faturas
          JOIN PEDI_110 i -- item de pedido de venda
            ON i.PEDIDO_VENDA = pf.PEDIDO
          WHERE 1=1
            {filtro_deposito} -- filtro_deposito
          GROUP BY
            pf.PEDIDO
          , pf.NFOK
          , pf.NFDEV
          , i.CD_IT_PE_NIVEL99
          , i.CD_IT_PE_GRUPO
          , i.CD_IT_PE_SUBGRUPO
          , i.CD_IT_PE_ITEM
        )
        , it_ped_q_qfat AS -- itens de pedidos com qtd e qtd faturada
        (
          SELECT
            pq.PEDIDO
          , pq.NFOK
          , pq.NFDEV
          , pq.REF
          , pq.TAM
          , pq.COR
          , pq.QTD
          , sum(COALESCE(inf.QTDE_ITEM_FATUR, 0)) QTD_FAT
          FROM it_ped_qtd pq -- itens de pedidos com qtd
          LEFT JOIN fatu_060 inf -- item de nf de saída
            ON inf.CH_IT_NF_NUM_NFIS = pq.NFOK
           AND inf.PEDIDO_VENDA = pq.PEDIDO
           AND inf.COD_CANCELAMENTO = 0
           AND inf.NIVEL_ESTRUTURA = 1
           AND inf.GRUPO_ESTRUTURA = pq.REF
           AND inf.SUBGRU_ESTRUTURA = pq.TAM
           AND inf.ITEM_ESTRUTURA = pq.COR
          GROUP BY
            pq.PEDIDO
          , pq.NFOK
          , pq.NFDEV
          , pq.REF
          , pq.TAM
          , pq.COR
          , pq.QTD
        )
        , it_ped_qtd_final AS -- itens de pedidos com qtd e qtd fat e devolvida
        (
          SELECT
            pq.PEDIDO
          , pq.NFOK
          , pq.NFDEV
          , pq.REF
          , pq.TAM
          , pq.COR
          , pq.QTD
          , pq.QTD_FAT
          , sum(COALESCE(inf.QUANTIDADE, 0)) QTD_DEV
          , pq.QTD - pq.QTD_FAT + sum(COALESCE(inf.QUANTIDADE, 0)) QTD_FINAL
          FROM it_ped_q_qfat pq -- itens de pedidos com qtd
          LEFT JOIN OBRF_015 inf -- item de nf de devolução
            ON inf.CAPA_ENT_NRDOC = pq.NFDEV
           AND inf.NUM_NOTA_ORIG = pq.NFOK
           AND inf.CODITEM_NIVEL99 = 1
           AND inf.CODITEM_GRUPO = pq.REF
           AND inf.CODITEM_SUBGRUPO = pq.TAM
           AND inf.CODITEM_ITEM = pq.COR
          GROUP BY
            pq.PEDIDO
          , pq.NFOK
          , pq.NFDEV
          , pq.REF
          , pq.TAM
          , pq.COR
          , pq.QTD
          , pq.QTD_FAT
          HAVING
            pq.QTD - pq.QTD_FAT + sum(COALESCE(inf.QUANTIDADE, 0)) > 0
        )
        , it_qtd AS -- itens de qtd final
        (
          SELECT
            pq.REF
          , pq.COR
          , pq.TAM
          , sum(pq.QTD_FINAL) QTD
          FROM it_ped_qtd_final pq -- itens de pedidos com qtd e qtd fat e dev
          LEFT JOIN BASI_220 t -- tamanhos
            ON t.TAMANHO_REF = pq.TAM
          GROUP BY
            pq.REF
          , pq.COR
          , t.ORDEM_TAMANHO
          , pq.TAM
          ORDER BY
            pq.REF
          , pq.COR
          , t.ORDEM_TAMANHO
          , pq.TAM
        )
        SELECT
          ped.*
        FROM it_qtd ped
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
