from utils.functions.models import rows_to_dict_list


def responsavel(cursor, todos, ordem, estagio, usuario, usuario_num):
    filtro_estagio = ''
    if estagio:
        filtro_estagio = '''--
            AND e.CODIGO_ESTAGIO = {}
        '''.format(estagio)

    filtro_usuario = ''
    sep = ''
    if usuario:
        filtro_usuario = '''--
            ( coalesce( u.USUARIO, '_' ) like '{}' )
        '''.format(usuario)
        sep = ' OR '
    if usuario_num:
        filtro_usuario += sep + '''--
            ( u.CODIGO_USUARIO = {} )
        '''.format(usuario_num)
    if filtro_usuario:
        filtro_usuario = 'AND ( {} )'.format(filtro_usuario)

    sql = """
        SELECT
          s.CODIGO_ESTAGIO
        , s.CODIGO_ESTAGIO || ' - ' || s.DESCRICAO ESTAGIO
        , s.CODIGO_USUARIO
        , CASE WHEN s.USUARIO IS NULL
          THEN '--SEM RESPONSAVEL--'
          ELSE s.USUARIO || ' ( ' || s.CODIGO_USUARIO || ' )'
          END USUARIO
        , CASE WHEN EXISTS (
            SELECT
              r.TIPO_MOVIMENTO
            FROM MQOP_006 r
            WHERE r.CODIGO_ESTAGIO = s.CODIGO_ESTAGIO
              AND r.CODIGO_USUARIO = s.CODIGO_USUARIO
              AND r.TIPO_MOVIMENTO IN (0, 1)
          )
          THEN 'X'
          ELSE ' ' END BL
        , CASE WHEN EXISTS (
            SELECT
              r.TIPO_MOVIMENTO
            FROM MQOP_006 r
            WHERE r.CODIGO_ESTAGIO = s.CODIGO_ESTAGIO
              AND r.CODIGO_USUARIO = s.CODIGO_USUARIO
              AND r.TIPO_MOVIMENTO IN (0, 2)
          )
          THEN 'X'
          ELSE ' ' END EL
        , CASE WHEN EXISTS (
            SELECT
              r.TIPO_MOVIMENTO
            FROM MQOP_006 r
            WHERE r.CODIGO_ESTAGIO = s.CODIGO_ESTAGIO
              AND r.CODIGO_USUARIO = s.CODIGO_USUARIO
              AND r.TIPO_MOVIMENTO = 3
          )
          THEN 'X'
          ELSE ' ' END CO
        , CASE WHEN EXISTS (
            SELECT
              r.TIPO_MOVIMENTO
            FROM MQOP_006 r
            WHERE r.CODIGO_ESTAGIO = s.CODIGO_ESTAGIO
              AND r.CODIGO_USUARIO = s.CODIGO_USUARIO
              AND r.TIPO_MOVIMENTO = 4
          )
          THEN 'X'
          ELSE ' ' END AO
        FROM (
          SELECT DISTINCT
            e.CODIGO_ESTAGIO
          , e.DESCRICAO
          , u.USUARIO
          , u.CODIGO_USUARIO
          FROM MQOP_005 e
          CROSS JOIN HDOC_030 u
        """
    if todos == 'e':
        sql += """
          LEFT JOIN MQOP_006 r
        """
    else:
        sql += """
          JOIN MQOP_006 r
        """
    sql += """
            ON r.CODIGO_ESTAGIO = e.CODIGO_ESTAGIO
           AND r.CODIGO_USUARIO = u.CODIGO_USUARIO
          --FROM MQOP_005 e
          --LEFT JOIN MQOP_006 r
        --    ON r.CODIGO_ESTAGIO = e.CODIGO_ESTAGIO
          --LEFT JOIN HDOC_030 u
        --    ON u.EMPRESA = 1
        --   AND u.CODIGO_USUARIO = r.CODIGO_USUARIO
          WHERE e.CODIGO_ESTAGIO <> 0
            AND u.ATIVO_INATIVO = 1
            {filtro_estagio} -- filtro_estagio
            {filtro_usuario} -- filtro_usuario
            AND SUBSTR(u.USUARIO, 1, 3) != 'A__'
            AND SUBSTR(u.USUARIO, 1, 8) != 'DEFAULT_'
            --AND ( _s is NULL OR e.CODIGO_ESTAGIO = _s )
            --AND ( ( coalesce( u.USUARIO, '_' ) like _s )
            --    OR ( _s is NOT NULL AND u.CODIGO_USUARIO = _s )
            --    )
        """
    if todos == 'a':
        sql += """
              AND u.CODIGO_USUARIO not in(1, 99001) -- DUOMO, Anselmo
              AND ( e.CODIGO_ESTAGIO < 7 OR
                    u.USUARIO not in ( 'ROSANGELA_PCP'
                                     , 'ALESSANDRA_PCP'
                                     , 'ADRIANA_PCP')
                  )
        """
    sql += """
          ORDER BY
        """
    if ordem == 'e':
        sql += '''
              e.CODIGO_ESTAGIO
            , u.USUARIO
        '''
    else:
        sql += '''
              u.USUARIO
            , e.CODIGO_ESTAGIO
        '''
    sql += """
        ) s
        """
    sql = sql.format(
        filtro_estagio=filtro_estagio,
        filtro_usuario=filtro_usuario,
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def responsavel_direitos(cursor, estagio, usuario_num):
    sql = """
        SELECT
          r.TIPO_MOVIMENTO
        FROM MQOP_006 r
        WHERE r.CODIGO_ESTAGIO = %s
          AND r.CODIGO_USUARIO = %s
        """
    cursor.execute(sql, (estagio, usuario_num))
    return rows_to_dict_list(cursor)


def responsavel_inclui_direitos(cursor, estagio, usuario_num, tipo_movimento):
    sql = """
        INSERT INTO SYSTEXTIL.MQOP_006
        ( CODIGO_ESTAGIO, CODIGO_USUARIO, TIPO_MOVIMENTO,
          FAMILIA_CELULA_PRODUCAO, FAMILIA_ESTAGIO)
        VALUES(%s, %s, %s, 0, 0)
        """
    try:
        cursor.execute(sql, (estagio, usuario_num, tipo_movimento))
        return True
    except Exception:
        return False


def responsavel_exclui_direitos(cursor, estagio, usuario_num, tipo_movimento):
    sql = """
        DELETE FROM SYSTEXTIL.MQOP_006
        WHERE CODIGO_ESTAGIO=%s
          AND CODIGO_USUARIO=%s
          AND TIPO_MOVIMENTO=%s
        """
    try:
        cursor.execute(sql, (estagio, usuario_num, tipo_movimento))
        return True
    except Exception:
        return False


def responsavel_altera_direitos(
        cursor, estagio, usuario_num, tipo_movimento_de, tipo_movimento_para):
    sql = """
        UPDATE SYSTEXTIL.MQOP_006
        SET TIPO_MOVIMENTO = %s
        WHERE CODIGO_ESTAGIO=%s
          AND CODIGO_USUARIO=%s
          AND TIPO_MOVIMENTO=%s
        """
    try:
        cursor.execute(sql, (
            tipo_movimento_para, estagio, usuario_num, tipo_movimento_de))
        return True
    except Exception:
        return False
