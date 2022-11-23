#!/usr/bin/env python3

import fdb
import time
from pprint import pprint

from db_password import (
    DBPASS_F1,
)


_DATABASES = {
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

    def connect_fdb(self, id, return_error=False):
        try:
            db = _DATABASES[id]

            self.con = fdb.connect(
                host=db['HOST'],
                port=db['PORT'],
                database=db['NAME'],
                user=db['USER'],
                password=db['PASSWORD'],
                sql_dialect=db['DIALECT'],
                charset=db['OPTIONS']['charset'],
            )

        except Exception as e:
            if return_error:
                return e
            else:
                raise e

    def get_cursor(self):
        self.cursor = self.con.cursor()

    def close(self):
        self.con.close()

    def execute(self, sql):
        self.cursor.execute(sql)

    def fetchall(self):
        return self.cursor.fetchall()

    def conecta_fdb_db(self, db_id):
        error = self.connect_fdb(db_id, return_error=True)

        if isinstance(error, Exception):
            return False, error
        else:
            try:
                self.get_cursor()
                self.close()
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

    def rotina(self):
        self.connect_fdb('f1')
        self.get_cursor()
        
        sql = """
            select
            pc.*
            from SCC_PLANOCONTASNOVO pc
        """
        self.execute(sql)

        data = self.fetchall()

        pprint(data[:3])

        self.close()


if __name__ == '__main__':
    main = Main()
    # main.test()
    # pprint(main.context)
    main.rotina()
