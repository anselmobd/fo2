from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor):
    sql = f"""
        SELECT
          vs.audsid
        , to_char(locks.sid) sid
        , to_char(vs.serial#) serial
        , round( locks.ctime/60, 2 ) lock_time_in_minutes
        --, vs.username oracle_user
        --, vs.osuser os_user
        , vs.program
        , vs.module
        , vs.action
        , vs.process
        , decode(
            locks.lmode
          , 1, NULL
          , 2, 'Row Share'
          , 3, 'Row Exclusive'
          , 4, 'Share'
          , 5, 'Share Row Exclusive'
          , 6, 'Exclusive'
          , 'None'
          ) lock_mode_held
        , decode(
            locks.request
          , 1, NULL
          , 2, 'Row Share'
          , 3, 'Row Exclusive'
          , 4, 'Share'
          , 5, 'Share Row Exclusive'
          , 6, 'Exclusive'
          , 'None'
          ) lock_mode_requested
        , decode(
            locks.TYPE
          , 'MR', 'Media Recovery'
          , 'RT', 'Redo Thread'
          , 'UN', 'User Name'
          , 'TX', 'Transaction'
          , 'TM', 'DML'
          , 'UL', 'PL/SQL User Lock'
          , 'DX', 'Distributed Xaction'
          , 'CF', 'Control File'
          , 'IS', 'Instance State'
          , 'FS', 'File Set'
          , 'IR', 'Instance Recovery'
          , 'ST', 'Disk Space Transaction'
          , 'TS', 'Temp Segment'
          , 'IV', 'Library Cache Invalidation'
          , 'LS', 'Log Start or Log Switch'
          , 'RW', 'Row Wait'
          , 'SQ', 'Sequence Number'
          , 'TE', 'Extend Table'
          , 'TT', 'Temp Table'
          , locks.TYPE
          ) lock_type
        --, objs.object_type || ':' || objs.owner || '-' || objs.object_name obj_type_owner_name
        , LISTAGG(
            DISTINCT
            objs.object_type || ':' || objs.owner || '-' || objs.object_name
          , ', '
          )
          WITHIN GROUP (ORDER BY objs.object_type, objs.owner, objs.object_name)
          obj_type_owner_name
        , st.SQL_ID 
        , st.piece
        , st.SQL_TEXT
        FROM v$session vs
        JOIN v$lock locks
          ON locks.sid = vs.sid
        JOIN all_objects objs
          ON objs.object_id = locks.id1
        JOIN all_tables tbls
          ON tbls.owner = objs.owner
        AND tbls.table_name = objs.object_name
        JOIN v$sqltext st
          ON st.address = vs.sql_address
        AND st.hash_value = vs.sql_hash_value
        WHERE objs.owner != 'SYS'
        --  AND locks.type = 'TM'
        GROUP BY
          vs.audsid
        , locks.sid
        , vs.serial#
        , locks.ctime
        -- , vs.username
        -- , vs.osuser
        , vs.program
        , vs.module
        , vs.action
        , vs.process
        , locks.lmode
        , locks.request
        , locks.TYPE
        , st.SQL_ID 
        , st.piece
        , st.SQL_TEXT
        ORDER BY
          lock_time_in_minutes DESC
        , locks.sid
        , vs.serial#
        , st.SQL_ID 
        , st.piece
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
