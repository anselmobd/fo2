from utils.functions.models import rows_to_dict_list_lower, GradeQtd


def grade_estoque(
        cursor, ref=None, dep=None, data_ini=None, tipo_grade=None,
        modelo=None):

    filtro_modelo = ''
    filtro_modelo_mask = ''
    if modelo is not None:
        filtro_modelo_mask = f'''--
            AND
              TRIM(
                LEADING '0' FROM (
                  REGEXP_REPLACE(
                    {{}},
                    '^[abAB]?([0-9]+)[a-zA-Z]*$',
                    '\\1'
                  )
                )
              ) = '{modelo}'
        '''

    teste_dep = ''
    if type(dep) is tuple:
        teste_dep = ",".join(map(str, dep))
        teste_dep = f" IN ({teste_dep})"
    else:
        teste_dep = f" = '{dep}'"

    filtro_data_ini = ''
    if data_ini is not None:
        filtro_data_ini = (
            "AND ee.DATA_MOVIMENTO >= "
            f"TO_DATE('{data_ini}', 'yyyy-mm-dd')"
        )

    if tipo_grade is None:
        tipo_grade = {
            't': 'c',  # tamanho como cadastrado
            'c': 'e',  # cores com estoque
        }

    # Grade de OP
    grade = GradeQtd(cursor)

    # tamanhos
    if tipo_grade['t'] == 'm':  # com movimento
        filtro_ref = ''
        if ref is not None:
            filtro_ref = f"AND ee.GRUPO_ESTRUTURA  = '{ref}'"
        if modelo is not None:
            filtro_modelo = filtro_modelo_mask.format('ee.GRUPO_ESTRUTURA')
        sql = f'''
            SELECT DISTINCT
              ee.SUBGRUPO_ESTRUTURA TAMANHO
            , tam.ORDEM_TAMANHO SEQUENCIA_TAMANHO
            FROM ESTQ_300_ESTQ_310 ee -- mov.de estoque em aberto e fechado
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = ee.SUBGRUPO_ESTRUTURA
            WHERE ee.NIVEL_ESTRUTURA = 1
              {filtro_ref} -- filtro_ref
              {filtro_modelo} -- filtro_modelo
              AND ee.CODIGO_DEPOSITO {teste_dep}
              {filtro_data_ini} -- filtro_data_ini
            ORDER BY
              2
        '''
    elif tipo_grade['t'] == 'e':  # com estoque
        filtro_ref = ''
        if ref is not None:
            filtro_ref = f"AND e.CDITEM_GRUPO  = '{ref}'"
        if modelo is not None:
            filtro_modelo = filtro_modelo_mask.format('e.CDITEM_GRUPO')
        sql = f'''
            SELECT DISTINCT
              e.CDITEM_SUBGRUPO TAMANHO
            , tam.ORDEM_TAMANHO SEQUENCIA_TAMANHO
            FROM ESTQ_040 e
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = e.CDITEM_SUBGRUPO
            WHERE e.CDITEM_NIVEL99 = 1
              {filtro_ref} -- filtro_ref
              {filtro_modelo} -- filtro_modelo
              AND e.DEPOSITO {teste_dep}
              AND e.QTDE_ESTOQUE_ATU <> 0
            ORDER BY
              2
        '''

    elif tipo_grade['t'] == 'c':  # como cadastrado
        filtro_ref = ''
        if ref is not None:
            filtro_ref = f"AND t.BASI030_REFERENC  = '{ref}'"
        if modelo is not None:
            filtro_modelo = filtro_modelo_mask.format('t.BASI030_REFERENC')
        sql = f'''
            SELECT DISTINCT
              t.TAMANHO_REF TAMANHO
            , tam.ORDEM_TAMANHO SEQUENCIA_TAMANHO
            FROM basi_020 t
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = t.TAMANHO_REF
            WHERE t.BASI030_NIVEL030 = 1
              {filtro_ref} -- filtro_ref
              {filtro_modelo} -- filtro_modelo
            ORDER BY
              2
        '''

    grade.col(
        id='TAMANHO',
        name='Tamanho',
        total='Total',
        forca_total=True,
        sql=sql,
    )

    # cores
    if tipo_grade['c'] == 'm':  # com movimento
        filtro_ref = ''
        if ref is not None:
            filtro_ref = f"AND ee.GRUPO_ESTRUTURA  = '{ref}'"
        if modelo is not None:
            filtro_modelo = filtro_modelo_mask.format('ee.GRUPO_ESTRUTURA')
        sql = f'''
            SELECT DISTINCT
              ee.ITEM_ESTRUTURA SORTIMENTO
            FROM ESTQ_300_ESTQ_310 ee -- mov. de estoque em aberto e fechado
            WHERE ee.NIVEL_ESTRUTURA = 1
              {filtro_ref} -- filtro_ref
              {filtro_modelo} -- filtro_modelo
              AND ee.CODIGO_DEPOSITO {teste_dep}
              {filtro_data_ini} -- filtro_data_ini
            ORDER BY
              ee.ITEM_ESTRUTURA
        '''
    elif tipo_grade['c'] == 'e':  # com estoque
        filtro_ref = ''
        if ref is not None:
            filtro_ref = f"AND e.CDITEM_GRUPO  = '{ref}'"
        if modelo is not None:
            filtro_modelo = filtro_modelo_mask.format('e.CDITEM_GRUPO')
        sql = f'''
            SELECT DISTINCT
              e.CDITEM_ITEM SORTIMENTO
            FROM ESTQ_040 e
            WHERE e.CDITEM_NIVEL99 = 1
              {filtro_ref} -- filtro_ref
              {filtro_modelo} -- filtro_modelo
              AND e.DEPOSITO {teste_dep}
              AND e.QTDE_ESTOQUE_ATU <> 0
            ORDER BY
              e.CDITEM_ITEM
        '''

    grade.row(
        id='SORTIMENTO',
        name='Cor',
        name_plural='Cores',
        total='Total',
        forca_total=True,
        sql=sql,
    )

    # sortimento
    filtro_ref = ''
    if ref is not None:
        filtro_ref = f"AND e.CDITEM_GRUPO  = '{ref}'"
    if modelo is not None:
        filtro_modelo = filtro_modelo_mask.format('e.CDITEM_GRUPO')
    sql = f'''
        SELECT
          e.CDITEM_SUBGRUPO TAMANHO
        , e.CDITEM_ITEM SORTIMENTO
        , SUM(e.QTDE_ESTOQUE_ATU) QUANTIDADE
        FROM ESTQ_040 e
        WHERE e.LOTE_ACOMP = 0
          AND e.CDITEM_NIVEL99 = 1
          {filtro_ref} -- filtro_ref
          {filtro_modelo} -- filtro_modelo
          AND e.DEPOSITO {teste_dep}
        GROUP BY
          e.CDITEM_SUBGRUPO
        , e.CDITEM_ITEM
        ORDER BY
          e.CDITEM_SUBGRUPO
        , e.CDITEM_ITEM
    '''

    grade.value(
        id='QUANTIDADE',
        sql=sql,
    )

    fields = grade.table_data['fields']
    data = grade.table_data['data']
    style = grade.table_data['style']

    result = (
        grade.table_data['header'],
        fields,
        data,
        style,
        grade.total,
    )

    return result
