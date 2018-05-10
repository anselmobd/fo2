from fo2.models import rows_to_dict_list

from lotes.models import *
from lotes.models.base import *


def responsavel(cursor, todos, ordem, estagio, usuario, usuario_num):
    sql = """
        SELECT
          s.CODIGO_ESTAGIO || ' - ' || s.DESCRICAO ESTAGIO
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
          LEFT JOIN MQOP_006 r
            ON r.CODIGO_ESTAGIO = e.CODIGO_ESTAGIO
          LEFT JOIN HDOC_030 u
            ON u.CODIGO_USUARIO = r.CODIGO_USUARIO
          WHERE e.CODIGO_ESTAGIO <> 0
            AND ( %s is NULL OR e.CODIGO_ESTAGIO = %s )
            AND ( ( coalesce( u.USUARIO, '_' ) like %s )
                OR ( %s is NOT NULL AND u.CODIGO_USUARIO = %s )
                )
        """
    if not todos:
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
    cursor.execute(sql, (estagio, estagio,
                         usuario, usuario_num, usuario_num))
    return rows_to_dict_list(cursor)
