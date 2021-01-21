from utils.functions.models import rows_to_dict_list_lower


def valor_mp(
        cursor, nivel, positivos, zerados, negativos, preco_zerado,
        deposito_compras):
    filtro_nivel = ''
    if nivel is not None:
        filtro_nivel = "AND e.CDITEM_NIVEL99 = {nivel}".format(nivel=nivel)

    filtro_positivos = ''
    if positivos == 's':
        filtro_positivos = "OR e.qtde_estoque_atu > 0"

    filtro_zerados = ''
    if zerados == 's':
        filtro_zerados = "OR e.qtde_estoque_atu = 0"

    filtro_negativos = ''
    if negativos == 's':
        filtro_negativos = "OR e.qtde_estoque_atu < 0"

    filtro_preco_zerado = ''
    if preco_zerado == 'n':
        filtro_preco_zerado = "AND rtc.PRECO_CUSTO_INFO != 0"

    filtro_deposito_compras = ''
    if deposito_compras == 'a':
        filtro_deposito_compras = """
            AND 1 = (
              CASE WHEN r.NIVEL_ESTRUTURA = 2 THEN
             CASE WHEN e.DEPOSITO = 202 THEN 1
             ELSE 0 END
              WHEN r.NIVEL_ESTRUTURA = 9 THEN
             CASE WHEN r.CONTA_ESTOQUE = 22 THEN
               CASE WHEN e.DEPOSITO = 212 THEN 1
               ELSE 0 END
             ELSE
               CASE WHEN e.DEPOSITO = 231 THEN 1
               ELSE 0 END
             END
              ELSE -- i.NIVEL_ESTRUTURA = 1
             CASE WHEN e.DEPOSITO in (101, 102) THEN 1
             ELSE 0 END
              END
            )
        """

    sql = '''
        SELECT
          e.cditem_nivel99 NIVEL
        , e.cditem_grupo REF
        , e.cditem_subgrupo TAM
        , e.cditem_item COR
        , r.CONTA_ESTOQUE || ' - ' || ce.DESCR_CT_ESTOQUE CONTA_ESTOQUE
        , e.deposito || ' - ' || d.DESCRICAO DEPOSITO
        , e.qtde_estoque_atu QTD
        , rtc.PRECO_CUSTO_INFO PRECO
        , e.qtde_estoque_atu * rtc.PRECO_CUSTO_INFO TOTAL
        , COALESCE(parm.ESTOQUE_MINIMO, 0) ESTOQUE_MINIMO
        , parm.TEMPO_REPOSICAO
        FROM ESTQ_040 e
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = e.cditem_nivel99
         AND r.REFERENCIA = e.cditem_grupo
        JOIN BASI_150 ce
          ON ce.CONTA_ESTOQUE = r.CONTA_ESTOQUE
        JOIN BASI_010 rtc
          ON rtc.NIVEL_ESTRUTURA = e.cditem_nivel99
         AND rtc.GRUPO_ESTRUTURA = e.cditem_grupo
         AND rtc.SUBGRU_ESTRUTURA = e.cditem_subgrupo
         AND rtc.ITEM_ESTRUTURA = e.cditem_item
        JOIN BASI_015 parm
          ON parm.NIVEL_ESTRUTURA = e.cditem_nivel99
         AND parm.GRUPO_ESTRUTURA = e.cditem_grupo
         AND parm.SUBGRU_ESTRUTURA = e.cditem_subgrupo
         AND parm.ITEM_ESTRUTURA = e.cditem_item
        LEFT JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = e.DEPOSITO
        WHERE 1=1
          {filtro_nivel} -- filtro_nivel
          AND (1=2
            {filtro_positivos} -- filtro_positivos
            {filtro_zerados} -- filtro_zerados
            {filtro_negativos} -- filtro_negativos
          )
          {filtro_preco_zerado} -- filtro_preco_zerado
          {filtro_deposito_compras} -- filtro_deposito_compras
        ORDER BY
          e.CDITEM_NIVEL99
        , e.cditem_grupo
        , e.cditem_subgrupo
        , e.cditem_item
        , e.DEPOSITO
    '''.format(
        filtro_nivel=filtro_nivel,
        filtro_positivos=filtro_positivos,
        filtro_zerados=filtro_zerados,
        filtro_negativos=filtro_negativos,
        filtro_preco_zerado=filtro_preco_zerado,
        filtro_deposito_compras=filtro_deposito_compras,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
