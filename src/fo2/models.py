import fdb

from django.db import models

from fo2.settings import DB_F1


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def cursorF1():
    con = fdb.connect(
        dsn='{}/{}:{}'.format(DB_F1['HOST'], DB_F1['PORT'], DB_F1['NAME']),
        user=DB_F1['USER'],
        password=DB_F1['PASSWORD'],
        charset=DB_F1['CHARSET']
        )
    return con.cursor()
