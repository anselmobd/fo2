from fo2.models import rows_to_dict_list

from lotes.models import *
from lotes.models.base import *


def responsavel(cursor, todos, ordem, estagio, usuario, usuario_num):
    sql = """
        SELECT
          e.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        , CASE WHEN u.USUARIO IS NULL
          THEN '--SEM RESPONSAVEL--'
          ELSE u.USUARIO || ' ( ' || u.CODIGO_USUARIO || ' )'
          END USUARIO
        FROM MQOP_005 e
        LEFT JOIN MQOP_006 r
          ON r.CODIGO_ESTAGIO = e.CODIGO_ESTAGIO
         AND r.TIPO_MOVIMENTO = 0
        LEFT JOIN HDOC_030 u
          ON u.CODIGO_USUARIO = r.CODIGO_USUARIO
        WHERE e.CODIGO_ESTAGIO <> 0
          AND ( %s is NULL OR e.CODIGO_ESTAGIO = %s )
          AND ( ( coalesce( u.USUARIO, '_' ) like %s )
              OR ( %s is NOT NULL AND u.CODIGO_USUARIO = %s )
              )
    """
    if not todos:
        sql = sql + """
              AND u.CODIGO_USUARIO <> 99001 -- Anselmo
              AND ( e.CODIGO_ESTAGIO < 7 OR
                    u.USUARIO not in ( 'ROSANGELA_PCP'
                                     , 'ALESSANDRA_PCP'
                                     , 'ADRIANA_PCP' )
                  )
        """
    sql = sql + """
        ORDER BY
    """
    if ordem == 'e':
        sql = sql + '''
              e.CODIGO_ESTAGIO
            , u.USUARIO
        '''
    else:
        sql = sql + '''
              u.USUARIO
            , e.CODIGO_ESTAGIO
        '''
    cursor.execute(sql, (estagio, estagio,
                         usuario, usuario_num, usuario_num))
    return rows_to_dict_list(cursor)
