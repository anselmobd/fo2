#!/usr/bin/env python3

import fdb
import time
from pprint import pprint

from db_password import (
    DBPASS_F1,
)

DATABASES = {
    'f1': {  # F1 e SCC
        'ENGINE': 'firebird',
        'NAME': '/dados/db/f1/f1.cdb',
        'USER': 'sysdba',
        'PASSWORD': DBPASS_F1,
        'HOST': 'localhost',
        'PORT': 23050,
        # 'HOST': '192.168.1.98',
        # 'PORT': 3050,
        'OPTIONS': {'charset': 'WIN1252'},
        'TIME_ZONE': None,
        'CONN_MAX_AGE': None,
        'AUTOCOMMIT': None,
        'DIALECT': 3,
    },
}


class Main():

    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)
        self.context = {}

    def connect_fdb(self, db_id, return_error=False):
        try:
            dbsett = DATABASES[db_id]

            self.conn = fdb.connect(
                host=dbsett['HOST'],
                port=dbsett['PORT'],
                database=dbsett['NAME'],
                user=dbsett['USER'],
                password=dbsett['PASSWORD'],
                sql_dialect=dbsett['DIALECT'],
                charset=dbsett['OPTIONS']['charset'],
            )

        except Exception as e:
            if return_error:
                return e
            else:
                raise e

    def conecta_fdb_db(self, db_id):
        error = self.connect_fdb(db_id, return_error=True)

        if isinstance(error, Exception):
            return False, error
        else:
            try:
                cursor = self.conn.cursor()
                self.conn.close()
                return True, None
            except Exception as e:
                return False, e

    def acessa_fdb_db(self, db_id):
        count = 0

        while count < 20:
            result, e = self.conecta_fdb_db(db_id)
            if result:
                self.context['msgs_ok'].append(f'Banco "{db_id}" acessível')
                break
            else:
                error = e
            count += 1
            time.sleep(0.5)

        if count != 0:
            self.context['msgs_erro'].append(
                f'({count}) Erro ao acessar banco "{db_id}" [{error}]')

    def test(self):
        self.context.update({
            'msgs_ok': [],
            'msgs_erro': [],
        })

        self.acessa_fdb_db('f1')

if __name__ == '__main__':
    main = Main()
    main.test()
    pprint(main.context)
