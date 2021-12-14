from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def rodando_a_segundos(cursor, segundos):
    sql = f"""
        WITH demorados AS
        (
        SELECT
          s.username
        , s.sid
        , s.serial# serial
        , s.last_call_et secs
        , q.sql_text
        from v$session s 
        join v$sqltext_with_newlines q
          on s.sql_address = q.address
        where status='ACTIVE'
          and type <>'BACKGROUND'
          and last_call_et > {segundos}
        order BY
          4 DESC
        , sid
        , serial#
        , q.piece
        )
        SELECT 
          d.*
        FROM demorados d
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def sessoes_travadoras(cursor):
    sql = f"""
        SELECT
          h.session_id Sessao_Travadora,
          ub.username Usuario_Travador,
          w.session_id Sessao_Esperando,
          uw.username Usuario_Esperando,
          w.lock_type,
          h.mode_held,
          w.mode_requested,
          w.lock_id1,
          w.lock_id2
        FROM
          dba_locks w,
          dba_locks h,
          v$session ub,
          v$session uw
        WHERE h.blocking_others = 'Blocking'
          AND h.mode_held != 'None'
          AND h.mode_held != 'Null'
          AND h.session_id = ub.sid
          AND w.mode_requested != 'None'
          AND w.lock_type = h.lock_type
          AND w.lock_id1 = h.lock_id1
          AND w.lock_id2 = h.lock_id2
          AND w.session_id = uw.sid
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def get_info_sessao(cursor, sessao_id):
    sql = f"""
        SELECT
          s.username
        , s.module
        , s.status
        , s.logon_time
        , s.PREV_EXEC_START
        , s.sid
        , s.serial# serial
        , s.machine
        , s.client_info
        from v$session s 
        WHERE 1=1
          AND s.sid = {sessao_id}
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
