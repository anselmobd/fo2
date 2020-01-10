import datetime

from fo2.models import rows_to_dict_list_lower


def estoque_na_data(cursor, num_doc, data=None, hora=None, deposito=None):

    data_sql = ''
    if data is not None:
        if hora is None:
            data_hora = data
        else:
            data_hora = datetime.datetime.combine(data, hora)
        data_sql = '''--
            TIMESTAMP '{}'
        '''.format(
            data_hora.strftime('%Y-%m-%d %H:%M:%S')
        )

    sql = '''
        WITH filtro AS
        ( SELECT
            e.deposito dep
          , e.cditem_nivel99 nivel
          , e.cditem_grupo ref
          , e.cditem_subgrupo tam
          , e.cditem_item cor
          , {data_sql} dt -- data do estoque
          , {num_doc} dtinv -- data do estoque em formato de numdoc de ajuste
          FROM estq_040 e
          LEFT JOIN BASI_220 ta
            ON ta.TAMANHO_REF = e.cditem_subgrupo
          WHERE e.deposito = {deposito}
            AND e.cditem_nivel99 = 1
            AND e.cditem_grupo < 'C0000'
            AND e.cditem_grupo = '5156U'
        --    AND e.cditem_subgrupo = 'P'
        --    AND e.cditem_item = '0000BR'
            AND e.lote_acomp = 0
          ORDER BY
            e.cditem_grupo
          , e.cditem_item
          , ta.ORDEM_TAMANHO
          , e.cditem_subgrupo
        )
        SELECT
          filtro.dep
        , filtro.ref
        , filtro.tam
        , filtro.cor
        , COALESCE(
            ( -- estoque de PAPBPG em 101
              SELECT
                sum(e.qtde_estoque_atu)
              FROM estq_040 e
              WHERE e.lote_acomp = 0
                AND e.deposito = filtro.dep
                AND e.cditem_nivel99 = 1
                AND e.cditem_grupo = filtro.ref
                AND e.cditem_subgrupo = filtro.tam
                AND e.cditem_item = filtro.cor
            )
          , 0 ) STQ
        , COALESCE(
            ( -- trans. normais de PAPBPG em 101 desde data
              SELECT
                sum(
                  CASE WHEN t.ENTRADA_SAIDA = 'S' THEN
                    -t.QUANTIDADE
                  ELSE t.QUANTIDADE
                  END
                ) QTD
              FROM ESTQ_300_ESTQ_310 t
              WHERE t.CODIGO_DEPOSITO = filtro.dep
                AND t.DATA_MOVIMENTO >= filtro.dt
                AND (t.NUMERO_DOCUMENTO < 702000000
                    OR t.NUMERO_DOCUMENTO > 702999999
                    )
                AND t.NIVEL_ESTRUTURA = 1
                AND t.GRUPO_ESTRUTURA = filtro.ref
                AND t.SUBGRUPO_ESTRUTURA = filtro.tam
                AND t.ITEM_ESTRUTURA = filtro.cor
            )
          , 0 ) TRANS
        , COALESCE(
            ( -- trans. de ajuste de PAPBPG em 101 desde data
              SELECT
                sum(
                  CASE WHEN t.ENTRADA_SAIDA = 'S' THEN
                    -t.QUANTIDADE
                  ELSE t.QUANTIDADE
                  END
                ) QTD
              FROM ESTQ_300_ESTQ_310 t
              WHERE t.CODIGO_DEPOSITO = filtro.dep
                AND t.NUMERO_DOCUMENTO >= filtro.dtinv
                AND t.NUMERO_DOCUMENTO <= 702999999
                AND t.NIVEL_ESTRUTURA = 1
                AND t.GRUPO_ESTRUTURA = filtro.ref
                AND t.SUBGRUPO_ESTRUTURA = filtro.tam
                AND t.ITEM_ESTRUTURA = filtro.cor
            )
          , 0 ) AJUSTE
        FROM filtro
    '''.format(
        data_sql=data_sql,
        num_doc=num_doc,
        deposito=deposito,
        )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
