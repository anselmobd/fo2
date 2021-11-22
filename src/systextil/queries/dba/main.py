from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def rodando_a_segundos(cursor, segundos):
    sql = f"""
        WITH demorados AS
        (
        SELECT
          s.username
        , s.sid
        , s.serial#
        , s.last_call_et/60 mins_running
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
