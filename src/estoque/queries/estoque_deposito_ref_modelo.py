from utils.models import rows_to_dict_list_lower


def estoque_deposito_ref_modelo(cursor, deposito, ref=None, modelo=None):
    filtro_ref = ''
    if ref is not None and ref != '-':
        filtro_ref = '''--
            AND rtc.GRUPO_ESTRUTURA = '{ref}'
        '''.format(
            ref=ref,
        )

    filtro_modelo = ''
    if modelo is not None and modelo != '-':
        if '-' in modelo:
            modelos = modelo.split('-')
            filtro_modelo = '''--
                AND
                  TO_NUMBER(
                    TRIM(
                      LEADING '0' FROM (
                        REGEXP_REPLACE(
                          rtc.GRUPO_ESTRUTURA,
                          '^0?[abAB]?([0-9]+)[a-zA-Z]*$',
                          '\\1'
                        )
                      )
                    )
                  ) >= TO_NUMBER('{modelo_ini}')
                AND
                  TO_NUMBER(
                    TRIM(
                      LEADING '0' FROM (
                        REGEXP_REPLACE(
                          rtc.GRUPO_ESTRUTURA,
                          '^0?[abAB]?([0-9]+)[a-zA-Z]*$',
                          '\\1'
                        )
                      )
                    )
                  ) <= TO_NUMBER('{modelo_fim}')
            '''.format(
                modelo_ini=modelos[0],
                modelo_fim=modelos[1],
            )
        else:
            filtro_modelo = '''--
                AND
                  TRIM(
                    LEADING '0' FROM (
                      REGEXP_REPLACE(
                        rtc.GRUPO_ESTRUTURA,
                        '^0?[abAB]?([0-9]+)[a-zA-Z]*$',
                        '\\1'
                      )
                    )
                  ) = '{modelo}'
            '''.format(
                modelo=modelo,
            )

    sql = '''
        SELECT
          i.MODELO
        , i.REF
        , i.COR
        , ta.ORDEM_TAMANHO
        , i.TAM
        , i.DEP
        , COALESCE(e.QTDE_ESTOQUE_ATU, 0) QTD
        FROM (
          SELECT
            TO_NUMBER(
              TRIM(
                LEADING '0' FROM (
                  REGEXP_REPLACE(
                    rtc.GRUPO_ESTRUTURA,
                    '^0?[abAB]?([0-9]+)[a-zA-Z]*$',
                    '\\1'
                  )
                )
              )
            ) MODELO
          , rtc.GRUPO_ESTRUTURA REF
          , rtc.SUBGRU_ESTRUTURA TAM
          , rtc.ITEM_ESTRUTURA COR
          , d.CODIGO_DEPOSITO DEP
          FROM BASI_010 rtc, BASI_205 d
          WHERE 1=1
            AND rtc.NIVEL_ESTRUTURA = 1
            AND d.CODIGO_DEPOSITO = '{deposito}'
            AND rtc.GRUPO_ESTRUTURA < 'C0000'
            AND REGEXP_LIKE (
                  rtc.GRUPO_ESTRUTURA
                , '^0?[abAB]?([0-9]+)[a-zA-Z]*$'
                )
            {filtro_ref} -- filtro_ref
            {filtro_modelo} -- filtro_modelo
        ) i
        LEFT JOIN BASI_220 ta
          ON ta.TAMANHO_REF = i.TAM
        LEFT JOIN ESTQ_040 e
          ON e.LOTE_ACOMP = 0
         AND e.CDITEM_NIVEL99 = 1
         AND e.CDITEM_GRUPO = i.REF
         AND e.CDITEM_SUBGRUPO = i.TAM
         AND e.CDITEM_ITEM = i.COR
         AND e.DEPOSITO = i.DEP
        ORDER BY
          i.MODELO
        , NLSSORT(i.REF,'NLS_SORT=BINARY_AI')
        , i.COR
        , ta.ORDEM_TAMANHO
    '''.format(
        deposito=deposito,
        filtro_ref=filtro_ref,
        filtro_modelo=filtro_modelo,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
