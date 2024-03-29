from pprint import pprint

from systextil.queries.produto.modelo import sql_modelostr_ref, sql_sele_modelostr_ref
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def pedido_faturavel_sortimento(
        cursor, deposito, data_de, data_ate, retorno='r',
        empresa=1, colecao=None):

    filtro_deposito = ''
    if deposito is not None and deposito != '':
        filtro_deposito = f''' --
            AND i.CODIGO_DEPOSITO = {deposito} '''

    filtro_colecao = ''
    if colecao is not None and colecao != '':
        filtro_colecao = f''' --
            AND r.COLECAO = {colecao} '''

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
            -- AND ped.DATA_ENTR_VENDA >= TO_DATE('2019-02-25','YYYY-MM-DD')
            {filtro_data_ate} -- filtro_data_ate
            -- AND ped.DATA_ENTR_VENDA <= TO_DATE('2020-03-29','YYYY-MM-DD')
            AND ped.CODIGO_EMPRESA = {empresa}
          GROUP BY
            ped.PEDIDO_VENDA
        )
        , ped_faturas AS -- pedidos e suas faturas
        (
          SELECT
            ped.PEDIDO_VENDA PEDIDO
          , fok.NUM_NOTA_FISCAL NFOK
          FROM ped_data_entr ped -- pedido de venda filtrado
          LEFT JOIN FATU_050 fok -- fatura
            ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
           AND fok.SITUACAO_NFISC = 1  -- 1=emitida; 2=cancelada
           AND fok.NUMERO_CAIXA_ECF = 0
        )
        , it_ped_qtd AS -- itens de pedidos com qtd
        (
          SELECT
            pf.PEDIDO
          , i.CD_IT_PE_GRUPO REF
          , i.CD_IT_PE_SUBGRUPO TAM
          , i.CD_IT_PE_ITEM COR
          , sum(i.QTDE_PEDIDA) QTD
          FROM ped_faturas pf -- pedidos e suas faturas
          JOIN PEDI_110 i -- item de pedido de venda
            ON i.PEDIDO_VENDA = pf.PEDIDO
          JOIN basi_030 r
            ON r.NIVEL_ESTRUTURA = 1
           AND r.REFERENCIA = i.CD_IT_PE_GRUPO
          WHERE 1=1
             --
            AND pf.NFOK IS NULL
            AND i.CD_IT_PE_NIVEL99 = 1
            {filtro_deposito} -- filtro_deposito
            {filtro_colecao} -- filtro_colecao
          GROUP BY
            pf.PEDIDO
          , i.CD_IT_PE_GRUPO
          , i.CD_IT_PE_SUBGRUPO
          , i.CD_IT_PE_ITEM
        )
    """
    if retorno == 'r':
        sql += """--
            , it_qtd AS -- itens de qtd final
            (
              SELECT
                pq.REF
              , pq.COR
              , pq.TAM
              , sum(pq.QTD) QTD
              FROM it_ped_qtd pq -- itens de ped com qtd e qtd fat e dev
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
    elif retorno == 'm':
        sql += f"""--
            , it_qtd AS -- itens de qtd final
            (
              SELECT
                {sql_sele_modelostr_ref('pq.REF')}
              , sum(pq.QTD) QTD
              FROM it_ped_qtd pq -- itens de ped com qtd e qtd fat e dev
              LEFT JOIN BASI_220 t -- tamanhos
                ON t.TAMANHO_REF = pq.TAM
              GROUP BY
                {sql_modelostr_ref('pq.REF')}
              ORDER BY
                1
            )
            SELECT
              ped.*
            FROM it_qtd ped
        """
    elif retorno == 'p':
        sql += f"""--
            , it_qtd AS -- itens de qtd final
            (
              SELECT
                ped.DATA_ENTR_VENDA DATA
              , pq.PEDIDO
              , c.CGC_9 CNPJ9
              , c.CGC_4 CNPJ4
              , c.CGC_2 CNPJ2
              , c.NOME_CLIENTE
              , sum(pq.QTD) QTD
              FROM it_ped_qtd pq -- itens de ped com qtd e qtd fat e dev
              JOIN PEDI_100 ped -- pedido de venda
                ON ped.PEDIDO_VENDA = pq.PEDIDO
              LEFT JOIN PEDI_010 c -- cliente - do pedido de venda
                ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
               AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
               AND c.CGC_2 = ped.CLI_PED_CGC_CLI2
              WHERE ped.CODIGO_EMPRESA = {empresa}
              GROUP BY
                ped.DATA_ENTR_VENDA
              , pq.PEDIDO
              , c.CGC_9
              , c.CGC_4
              , c.CGC_2
              , c.NOME_CLIENTE
              ORDER BY
                ped.DATA_ENTR_VENDA
              , pq.PEDIDO
            )
            SELECT
              ped.*
            FROM it_qtd ped
        """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
