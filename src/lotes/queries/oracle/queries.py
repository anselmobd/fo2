from pprint import pprint


def oracle_existe_seq(cursor, owner, name):
    try:
        sql = f'''
            SELECT
              s.SEQUENCE_NAME
            FROM ALL_SEQUENCES s
            WHERE s.SEQUENCE_OWNER = '{owner}'
              AND s.SEQUENCE_NAME = '{name}'
        '''
        data = list(cursor.execute(sql))
        return data[0][0] == name
    except Exception:
        return False


def oracle_existe_table(cursor, owner, name):
    try:
        sql = f'''
            SELECT
              t.TABLE_NAME
            FROM ALL_TABLES t
            WHERE 1=1
              AND t.OWNER = '{owner}'
              AND t.TABLE_NAME = '{name}'
        '''
        data = list(cursor.execute(sql))
        return data[0][0] == name
    except Exception:
        return False

def oracle_existe_col(cursor, table, column):
    try:
        sql = f'''
            select
                column_name
            from user_tab_cols
            where table_name = '{table}'
              and column_name = '{column}'
        '''
        data = list(cursor.execute(sql))
        return data[0][0] == column
    except Exception:
        return False

def oracle_existe_trigger_sql(cursor, owner, table, trigger):
    return f'''
        SELECT
          t.TRIGGER_NAME
        FROM ALL_TRIGGERS t
        WHERE 1=1
          AND t.OWNER = '{owner}'
          AND t.TRIGGER_NAME = '{trigger}'
          AND t.TABLE_NAME = '{table}'
          AND t.STATUS = 'ENABLED'
    '''

def oracle_existe_trigger(cursor, owner, table, trigger):
    try:
        sql = oracle_existe_trigger_sql(cursor, owner, table, trigger)
        data = list(cursor.execute(sql))
        return data[0][0] == trigger
    except Exception:
        return False

def oracle_existem_triggers(cursor, owner, tables_triggers):
    sql_list = []
    for table, trigger in tables_triggers:
        sql = oracle_existe_trigger_sql(
            cursor, owner, table, trigger)
        sql_list = ['\n UNION \n'.join(sql_list+[sql])]
    sql_union = sql_list[0]

    try:
        data = list(cursor.execute(sql_union))
        return len(data) == len(tables_triggers)
    except Exception:
        return False

