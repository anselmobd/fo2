from utils.functions.models import GradeQtd

from utils.functions import arg_def


def op_sortimento(cursor, **kwargs):
    header, fields, data, total = op_sortimentos(cursor, **kwargs)
    return header, fields, data


def op_sortimentos(cursor, **kwargs):
    '''
    op: Apenas determinada OP
        >None - Todas
    tipo:>t - Todos os lotes
          a - Ainda não produzido / não finalizado
          fpnf - finalizado, de pedido, não faturado
          apf - a produzir, de pedido faturado
          p - Perda
          c - Conserto
          s - Segunda qualidade
          acd - estocada; "a", no CD (estágios 57 e 63)
          ap - em produção; "a", não no CD (estágios não 57 e 63)
    descr_sort: False - Apenas código do sortimento (cor)
               >True - Descrição junto ao código do sortimento (cor)
    modelo: Filtra PA, PB ou PG de determinado modelo_inform
           >None - QQ referência
    referencia: Filtra referência
               >None - QQ referência
    situacao:>None - Todas
              c - OP cancelada
              a - OP não cancelado (ativa)
    tipo_ref:>None - Todas
              a - PA
              g - PG
              b - import pdb; pdb.set_trace()
              p - PG ou PB
              v - PA, PG ou PB
              m - MD ou outros não "PA, PG ou PB"
    tipo_alt:>None - Todas
              e - OP de expedição (PA com alternativa em (10, 50) ou (60, 100))
              p - OP não de expedição
    total: True - totaliza grade
          >None, False - não totaliza
    '''
    def argdef(arg, default):
        return arg_def(kwargs, arg, default)

    op = argdef('op', None)
    tipo = argdef('tipo', 't')
    descr_sort = argdef('descr_sort', True)
    modelo = argdef('modelo', None)
    referencia = argdef('referencia', None)
    situacao = argdef('situacao', None)
    tipo_ref = argdef('tipo_ref', None)
    tipo_alt = argdef('tipo_alt', None)
    total = argdef('total', None)

    filtra_op = ''
    if op is not None:
        filtra_op = 'AND lote.ORDEM_PRODUCAO = {}'.format(op)

    filtra_modelo = ''
    if modelo is not None:
        filtra_modelo = """--
            AND TRIM( LEADING '0' FROM
                  REGEXP_REPLACE(
                    o.REFERENCIA_PECA,
                    '^[abAB]?([^a-zA-Z]+)[a-zA-Z]*$',
                    '\\1'
                  )
                ) = '{}'
        """.format(modelo)

    filtra_referencia = ''
    if referencia is not None:
        filtra_referencia = """--
            AND o.REFERENCIA_PECA = '{}'
        """.format(referencia)

    filtra_situacao = ''
    if situacao is not None:
        if situacao == 'a':
            filtra_situacao = "AND (NOT (o.SITUACAO = 9))"
        elif situacao == 'c':
            filtra_situacao = "AND o.SITUACAO = 9"

    filtro_tipo_ref = ''
    if tipo_ref is not None:
        if tipo_ref == 'a':
            filtro_tipo_ref = "AND o.REFERENCIA_PECA < 'A0000'"
        elif tipo_ref == 'g':
            filtro_tipo_ref = "AND o.REFERENCIA_PECA like 'A%'"
        elif tipo_ref == 'b':
            filtro_tipo_ref = "AND o.REFERENCIA_PECA like 'B%'"
        elif tipo_ref == 'p':
            filtro_tipo_ref = "AND (o.REFERENCIA_PECA like 'A%' OR " \
                "o.REFERENCIA_PECA like 'B%')"
        elif tipo_ref == 'v':
            filtro_tipo_ref = "AND o.REFERENCIA_PECA < 'C0000'"
        elif tipo_ref == 'm':
            filtro_tipo_ref = "AND o.REFERENCIA_PECA >= 'C0000'"

    filtro_tipo_alt = ''
    if tipo_alt is not None:
        if tipo_alt == 'e':
            filtro_tipo_alt = '''--
                AND o.REFERENCIA_PECA < 'A0000'
                AND (  (o.ALTERNATIVA_PECA > 10 AND o.ALTERNATIVA_PECA < 50)
                    OR (o.ALTERNATIVA_PECA > 60 AND o.ALTERNATIVA_PECA < 100)
                    )
            '''
        elif tipo_alt == 'p':
            filtro_tipo_alt = '''--
                AND NOT (
                  o.REFERENCIA_PECA < 'A0000'
                  AND (  (o.ALTERNATIVA_PECA > 10 AND o.ALTERNATIVA_PECA < 50)
                      OR (o.ALTERNATIVA_PECA > 60 AND o.ALTERNATIVA_PECA < 100)
                      )
                )
            '''

    filtro_especifico = ''
    if tipo == 'a':  # Ainda não produzido / não finalizado
        filtro_especifico = \
            "AND (lote.QTDE_DISPONIVEL_BAIXA > 0 OR lote.QTDE_CONSERTO > 0)"
    elif tipo == 'acd':  # Ainda não produzido / lotes no CD
        filtro_especifico = """--
            AND (lote.QTDE_DISPONIVEL_BAIXA > 0 OR lote.QTDE_CONSERTO > 0)
            AND lote.CODIGO_ESTAGIO IN (57, 63) -- filtro_especifico
            """
    elif tipo == 'ap':  # Ainda não produzido / lotes em produção
        filtro_especifico = """--
            AND (lote.QTDE_DISPONIVEL_BAIXA > 0 OR lote.QTDE_CONSERTO > 0)
            AND lote.CODIGO_ESTAGIO NOT IN (57, 63) -- filtro_especifico
            """

    grade_args = {}
    if total is not None:
        grade_args = {
            'total': total,
            'forca_total': True,
        }

    # Grade de OP
    grade = GradeQtd(cursor)

    # tamanhos
    grade.col(
        id='TAMANHO',
        name='Tamanho',
        **grade_args,
        sql='''
            SELECT DISTINCT
              lote.PROCONF_SUBGRUPO TAMANHO
            , tam.ORDEM_TAMANHO SEQUENCIA_TAMANHO
            FROM PCPC_040 lote
            JOIN PCPC_020 o
              ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
            WHERE 1=1
              {filtro_especifico} -- filtro_especifico
              {filtra_op} -- filtra_op
              {filtra_modelo} -- filtra_modelo
              {filtra_referencia} -- filtra_referencia
              {filtra_situacao} -- filtra_situacao
              {filtro_tipo_ref} -- filtro_tipo_ref
              {filtro_tipo_alt} -- filtro_tipo_alt
            ORDER BY
              2
        '''.format(
            filtro_especifico=filtro_especifico,
            filtra_op=filtra_op,
            filtra_modelo=filtra_modelo,
            filtra_referencia=filtra_referencia,
            filtra_situacao=filtra_situacao,
            filtro_tipo_ref=filtro_tipo_ref,
            filtro_tipo_alt=filtro_tipo_alt,
        )
    )

    # cores
    sql = '''
        SELECT
          lote.PROCONF_ITEM SORTIMENTO
    '''
    if descr_sort:
        sql += '''
            , lote.PROCONF_ITEM || ' - ' || max( p.DESCRICAO_15 ) DESCR
        '''
    else:
        sql += '''
            , lote.PROCONF_ITEM DESCR
        '''
    sql += '''
        FROM PCPC_040 lote
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
    '''
    if descr_sort:
        sql += '''
            LEFT JOIN basi_010 p
              ON p.NIVEL_ESTRUTURA = 1
             AND p.GRUPO_ESTRUTURA = lote.PROCONF_GRUPO
             AND p.ITEM_ESTRUTURA = lote.PROCONF_ITEM
        '''
    sql += '''
        WHERE 1=1
          {filtro_especifico} -- filtro_especifico
          {filtra_op} -- filtra_op
          {filtra_modelo} -- filtra_modelo
          {filtra_referencia} -- filtra_referencia
          {filtra_situacao} -- filtra_situacao
          {filtro_tipo_ref} -- filtro_tipo_ref
          {filtro_tipo_alt} -- filtro_tipo_alt
        GROUP BY
          lote.PROCONF_ITEM
        ORDER BY
          2
    '''.format(
        filtro_especifico=filtro_especifico,
        filtra_op=filtra_op,
        filtra_modelo=filtra_modelo,
        filtra_referencia=filtra_referencia,
        filtra_situacao=filtra_situacao,
        filtro_tipo_ref=filtro_tipo_ref,
        filtro_tipo_alt=filtro_tipo_alt,
    )
    grade.row(
        id='SORTIMENTO',
        facade='DESCR',
        name='Cor',
        name_plural='Cores',
        **grade_args,
        sql=sql
        )

    if tipo == 't':  # Total a produzir / programado
        # sortimento
        grade.value(
            id='QUANTIDADE',
            sql='''
                SELECT
                  lote.PROCONF_SUBGRUPO TAMANHO
                , lote.PROCONF_ITEM SORTIMENTO
                , sum(lote.QTDE_PECAS_PROG ) QUANTIDADE
                FROM PCPC_040 lote
                LEFT JOIN BASI_220 tam
                  ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
                WHERE 1=1
                  {filtra_op} -- filtra_op
                  AND lote.SEQUENCIA_ESTAGIO
                      = COALESCE(
                          (
                            SELECT
                              MIN(ulote.SEQUENCIA_ESTAGIO)
                            FROM PCPC_040 ulote
                            WHERE ulote.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
                              AND ulote.ORDEM_CONFECCAO = lote.ORDEM_CONFECCAO
                            GROUP BY
                              ulote.ORDEM_PRODUCAO
                            , ulote.ORDEM_CONFECCAO
                          )
                        , 0)
                GROUP BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_SUBGRUPO
                , lote.PROCONF_ITEM
                ORDER BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_ITEM
            '''.format(
                filtra_op=filtra_op,
            )
        )

    # Ainda não produzido / não finalizado
    # Ainda não produzido / no CD
    # Ainda não produzido / não no CD
    elif tipo in ('a', 'acd', 'ap'):
        sql = '''
            WITH opl AS
            (
            SELECT distinct
              o.ORDEM_PRODUCAO
            , lote.SEQ_OPERACAO
            FROM pcpc_040 lote
            JOIN PCPC_020 o
              ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
            WHERE 1=1
              {filtro_especifico} -- filtro_especifico
              {filtra_op} -- filtra_op
              {filtra_modelo} -- filtra_modelo
              {filtra_referencia} -- filtra_referencia
              {filtra_situacao} -- filtra_situacao
              {filtro_tipo_ref} -- filtro_tipo_ref
              {filtro_tipo_alt} -- filtro_tipo_alt
            )
            SELECT
              l.PROCONF_SUBGRUPO TAMANHO
            , l.PROCONF_ITEM SORTIMENTO
            , SUM( l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO ) QUANTIDADE
            FROM pcpc_040 l
            JOIN opl
              ON opl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
             AND opl.SEQ_OPERACAO = l.SEQ_OPERACAO
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
            GROUP BY
              tam.ORDEM_TAMANHO
            , l.PROCONF_SUBGRUPO
            , l.PROCONF_ITEM
            ORDER BY
              tam.ORDEM_TAMANHO
            , l.PROCONF_ITEM
        '''.format(
            filtro_especifico=filtro_especifico,
            filtra_op=filtra_op,
            filtra_modelo=filtra_modelo,
            filtra_referencia=filtra_referencia,
            filtra_situacao=filtra_situacao,
            filtro_tipo_ref=filtro_tipo_ref,
            filtro_tipo_alt=filtro_tipo_alt,
        )
        grade.value(
            id='QUANTIDADE',
            sql=sql
        )

    elif tipo == 'fpnf':  # finalizado, de pedido, não faturado
        sql = '''
            WITH opl AS
            (
            SELECT
              o.ORDEM_PRODUCAO
            , SUM( lote.QTDE_DISPONIVEL_BAIXA + lote.QTDE_CONSERTO ) QTD_A_PROD
            FROM pcpc_040 lote
            JOIN PCPC_020 o
              ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
            LEFT JOIN PEDI_100 ped -- pedido de venda
              ON ped.PEDIDO_VENDA = o.PEDIDO_VENDA
             AND ped.STATUS_PEDIDO <> 5 -- não cancelado
            LEFT JOIN FATU_050 fok
              ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
             AND fok.SITUACAO_NFISC <> 2  -- cancelada
            WHERE 1=1
              {filtro_especifico} -- filtro_especifico
              {filtra_op} -- filtra_op
              {filtra_modelo} -- filtra_modelo
              {filtra_referencia} -- filtra_referencia
              {filtra_situacao} -- filtra_situacao
              {filtro_tipo_ref} -- filtro_tipo_ref
              {filtro_tipo_alt} -- filtro_tipo_alt
              AND o.PEDIDO_VENDA <> 0
              AND ped.PEDIDO_VENDA IS NOT NULL
              AND fok.NUM_NOTA_FISCAL IS NULL
            GROUP BY
              o.ORDEM_PRODUCAO
            )
            SELECT
              l.PROCONF_SUBGRUPO TAMANHO
            , l.PROCONF_ITEM SORTIMENTO
            , SUM( l.QTDE_PECAS_PROD ) QUANTIDADE
            FROM pcpc_040 l
            JOIN opl
              ON opl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
             AND opl.QTD_A_PROD = 0 -- OP finalizada
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
            GROUP BY
              tam.ORDEM_TAMANHO
            , l.PROCONF_SUBGRUPO
            , l.PROCONF_ITEM
            ORDER BY
              tam.ORDEM_TAMANHO
            , l.PROCONF_ITEM
        '''.format(
            filtro_especifico=filtro_especifico,
            filtra_op=filtra_op,
            filtra_modelo=filtra_modelo,
            filtra_referencia=filtra_referencia,
            filtra_situacao=filtra_situacao,
            filtro_tipo_ref=filtro_tipo_ref,
            filtro_tipo_alt=filtro_tipo_alt,
        )
        grade.value(
            id='QUANTIDADE',
            sql=sql,
        )

    elif tipo == 'apf':  # a produzir, de pedido faturado
        sql = '''
            WITH opl AS
            (
            SELECT
              o.ORDEM_PRODUCAO
            FROM pcpc_040 lote
            JOIN PCPC_020 o
              ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
            LEFT JOIN PEDI_100 ped -- pedido de venda
              ON ped.PEDIDO_VENDA = o.PEDIDO_VENDA
             AND ped.STATUS_PEDIDO <> 5 -- não cancelado
            LEFT JOIN FATU_050 fok
              ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
             AND fok.SITUACAO_NFISC <> 2  -- cancelada
            WHERE 1=1
              {filtro_especifico} -- filtro_especifico
              {filtra_op} -- filtra_op
              {filtra_modelo} -- filtra_modelo
              {filtra_referencia} -- filtra_referencia
              {filtra_situacao} -- filtra_situacao
              {filtro_tipo_ref} -- filtro_tipo_ref
              {filtro_tipo_alt} -- filtro_tipo_alt
              AND o.PEDIDO_VENDA <> 0
              AND ped.PEDIDO_VENDA IS NOT NULL
              AND fok.NUM_NOTA_FISCAL IS NOT NULL
            GROUP BY
              o.ORDEM_PRODUCAO
            )
            SELECT
              l.PROCONF_SUBGRUPO TAMANHO
            , l.PROCONF_ITEM SORTIMENTO
            , SUM( l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO ) QUANTIDADE
            FROM pcpc_040 l
            JOIN opl
              ON opl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
            GROUP BY
              tam.ORDEM_TAMANHO
            , l.PROCONF_SUBGRUPO
            , l.PROCONF_ITEM
            ORDER BY
              tam.ORDEM_TAMANHO
            , l.PROCONF_ITEM
        '''.format(
            filtro_especifico=filtro_especifico,
            filtra_op=filtra_op,
            filtra_modelo=filtra_modelo,
            filtra_referencia=filtra_referencia,
            filtra_situacao=filtra_situacao,
            filtro_tipo_ref=filtro_tipo_ref,
            filtro_tipo_alt=filtro_tipo_alt,
        )
        grade.value(
            id='QUANTIDADE',
            sql=sql,
        )

    elif tipo == 'p':  # Perda
        # sortimento
        grade.value(
            id='QUANTIDADE',
            sql='''
                SELECT
                  lote.PROCONF_SUBGRUPO TAMANHO
                , lote.PROCONF_ITEM SORTIMENTO
                , sum(lote.QTDE_PERDAS ) QUANTIDADE
                FROM PCPC_040 lote
                LEFT JOIN BASI_220 tam
                  ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
                WHERE 1=1
                  {filtra_op} -- filtra_op
                GROUP BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_SUBGRUPO
                , lote.PROCONF_ITEM
                ORDER BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_ITEM
            '''.format(
                filtra_op=filtra_op,
            )
        )

    elif tipo == 'c':  # Conserto
        # sortimento
        grade.value(
            id='QUANTIDADE',
            sql='''
                SELECT
                  lote.PROCONF_SUBGRUPO TAMANHO
                , lote.PROCONF_ITEM SORTIMENTO
                , sum(lote.QTDE_CONSERTO ) QUANTIDADE
                FROM PCPC_040 lote
                LEFT JOIN BASI_220 tam
                  ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
                WHERE 1=1
                  AND lote.CODIGO_ESTAGIO <> 63
                  {filtra_op} -- filtra_op
                GROUP BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_SUBGRUPO
                , lote.PROCONF_ITEM
                ORDER BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_ITEM
            '''.format(
                filtra_op=filtra_op,
            )
        )

    elif tipo == 's':  # Segunda qualidade
        # sortimento
        grade.value(
            id='QUANTIDADE',
            sql='''
                SELECT
                  lote.PROCONF_SUBGRUPO TAMANHO
                , lote.PROCONF_ITEM SORTIMENTO
                , sum(lote.QTDE_PECAS_2A ) QUANTIDADE
                FROM PCPC_040 lote
                LEFT JOIN BASI_220 tam
                  ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
                WHERE 1=1
                  {filtra_op} -- filtra_op
                  AND lote.SEQUENCIA_ESTAGIO
                      = COALESCE(
                          (
                            SELECT
                              MAX(ulote.SEQUENCIA_ESTAGIO)
                            FROM PCPC_040 ulote
                            WHERE ulote.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
                              AND ulote.ORDEM_CONFECCAO = lote.ORDEM_CONFECCAO
                              AND ulote.QTDE_PECAS_2A > 0
                            GROUP BY
                              ulote.ORDEM_PRODUCAO
                            , ulote.ORDEM_CONFECCAO
                          )
                        , 0)
                GROUP BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_SUBGRUPO
                , lote.PROCONF_ITEM
                ORDER BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_ITEM
            '''.format(
                filtra_op=filtra_op,
            )
        )

    fields = grade.table_data['fields']
    data = grade.table_data['data']
    if total is None:
        result = (
            grade.table_data['header'],
            fields,
            data,
            grade.total,
        )
    else:
        result = (
            grade.table_data['header'],
            fields,
            data,
            grade.table_data['style'],
            grade.total,
        )

    return result
