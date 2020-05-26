from utils.functions.models import rows_to_dict_list_lower


def referencia_deposito(cursor, modelo, todos=True, deposito='A00'):
    filtro_todos = ''
    if not todos:  # apenas aqueles que tem alguma quantidade
        filtro_todos = ''' --
            AND (sel.ESTOQUE <> 0 OR sel.FALTA <> 0)
        '''

    filtro_modelo = ''
    if modelo != '' and modelo is not None:
        filtro_modelo = '''--
            AND
              TRIM(
                LEADING '0' FROM (
                  REGEXP_REPLACE(
                    rtc.GRUPO_ESTRUTURA,
                    '^[abAB]?([0-9]+)[a-zA-Z]*$',
                    '\\1'
                  )
                )
              ) = '{modelo}'
        '''.format(
            modelo=modelo,
        )

    filtro_deposito = ''
    if deposito is not None and deposito != '':
        if deposito == 'A00':
            filtro_deposito = "AND d.CODIGO_DEPOSITO IN (101, 102, 122, 231)"
        else:
            filtro_deposito = "AND d.CODIGO_DEPOSITO = '{deposito}'".format(
                deposito=deposito)

    sql = '''
        SELECT
          sel.*
        FROM (
        SELECT
          rd.REF
        , rd.DEP
        , sum(
            CASE WHEN COALESCE(est.QTDE_ESTOQUE_ATU, 0) <= 0 THEN 0
            ELSE COALESCE(est.QTDE_ESTOQUE_ATU, 0) END
          ) ESTOQUE
        , sum(
            CASE WHEN COALESCE(est.QTDE_ESTOQUE_ATU, 0) >= 0 THEN 0
            ELSE COALESCE(est.QTDE_ESTOQUE_ATU, 0) END
          ) FALTA
        , sum(coalesce(est.QTDE_ESTOQUE_ATU, 0)) SOMA
        FROM (
          SELECT DISTINCT
            i.REF
          , i.DEP
          FROM (
            SELECT
              rtc.GRUPO_ESTRUTURA REF
            , rtc.SUBGRU_ESTRUTURA TAM
            , rtc.ITEM_ESTRUTURA COR
            , d.CODIGO_DEPOSITO DEP
            FROM BASI_010 rtc, BASI_205 d
            WHERE 1=1
              AND rtc.NIVEL_ESTRUTURA = 1
              AND rtc.GRUPO_ESTRUTURA < 'C0000'
              {filtro_deposito} -- filtro_deposito
              {filtro_modelo} -- filtro_modelo
          ) i
          LEFT JOIN ESTQ_040 e
            ON e.LOTE_ACOMP = 0
           AND e.CDITEM_NIVEL99 = 1
           AND e.CDITEM_GRUPO = i.REF
           AND e.CDITEM_SUBGRUPO = i.TAM
           AND e.CDITEM_ITEM = i.COR
           AND e.DEPOSITO = i.DEP
           AND e.QTDE_ESTOQUE_ATU <> 0
          LEFT JOIN ESTQ_300_ESTQ_310 m -- movimentação de estoque
            ON m.NIVEL_ESTRUTURA = 1
           AND m.GRUPO_ESTRUTURA = i.REF
           AND m.SUBGRUPO_ESTRUTURA = i.TAM
           AND m.ITEM_ESTRUTURA = i.COR
           AND m.CODIGO_DEPOSITO = i.DEP
          WHERE (  e.DEPOSITO IS NOT NULL
                OR m.CODIGO_DEPOSITO IS NOT NULL
                )
        ) rd
        LEFT JOIN ESTQ_040 est
          ON est.LOTE_ACOMP = 0
         AND est.CDITEM_NIVEL99 = 1
         AND est.CDITEM_GRUPO = rd.REF
         AND est.DEPOSITO = rd.DEP
         AND est.QTDE_ESTOQUE_ATU <> 0
        GROUP BY
          rd.DEP
        , rd.REF
        ORDER BY
          rd.DEP
        , NLSSORT(rd.REF,'NLS_SORT=BINARY_AI')
        ) sel
        WHERE 1=1
          {filtro_todos} -- filtro_todos
    '''.format(
        filtro_deposito=filtro_deposito,
        filtro_modelo=filtro_modelo,
        filtro_todos=filtro_todos,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
