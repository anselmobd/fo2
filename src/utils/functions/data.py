import time
import fdb
from pprint import pprint


def search_in_dict_fields(search, row, *fields, **params):
    ignore_case = params.get('ignore_case', True)
    for part in search.split():
        for field in fields:
            pattern = part.lower() if ignore_case else part
            value = row[field].lower() if ignore_case else row[field]
            if pattern in value:
                return True
    return False


def filtered_data_fields(search, data, *fields, **params):
    result = []
    for row in data:
        if search_in_dict_fields(search, row, *fields, **params):
            result.append(row)
    return result


def connect_fdb(databases, db_id, erros=[]):

    def connect(databases, db_id):
        try:
            db_dict = databases[db_id]

            conn = fdb.connect(
                host=db_dict['HOST'],
                port=db_dict['PORT'],
                database=db_dict['NAME'],
                user=db_dict['USER'],
                password=db_dict['PASSWORD'],
                sql_dialect=db_dict['DIALECT'],
                charset=db_dict['OPTIONS']['charset'],
            )
            return True, conn

        except Exception as e:
            return False, e

    count = 0

    while count < 20:
        result, conn = connect(databases, db_id)
        if result:
            return conn
        else:
            erros.append(conn)
        count += 1
        time.sleep(0.5)

    return None
