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
        self.test_context = {
            'msgs_ok': [],
            'msgs_erro': [],
        }

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
            # help(self.con)
        except Exception as e:
            if return_error:
                return e
            else:
                raise e

    def set_cursor(self):
        self.cursor = self.con.cursor()
        # help(self.cursor)
        # raise SystemExit

    def close(self):
        self.con.close()

    def execute(self, sql):
        self.cursor.execute(sql)

    def executemany(self, sql, list_tuples):
        # "insert into languages (name, year_released) values (?, ?)"
        self.cursor.executemany(sql, list_tuples)

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def itermap(self):
        return self.cursor.itermap()

    def commit(self):
        return self.con.commit()

    def rollback(self):
        return self.con.rollback()

    def conecta_fdb_db(self, db_id):
        error = self.connect_fdb(db_id, return_error=True)

        if isinstance(error, Exception):
            return False, error
        else:
            try:
                self.set_cursor()
                self.close()
                return True, None
            except Exception as e:
                return False, e

    def acessa_fdb_db(self, db_id):
        count = 0

        while count < 20:
            result, e = self.conecta_fdb_db(db_id)
            if result:
                self.test_context['msgs_ok'].append(f'Banco "{db_id}" acessível')
                break
            else:
                error = e
            count += 1
            time.sleep(0.5)

        if count != 0:
            self.test_context['msgs_erro'].append(
                f'({count}) Erro ao acessar banco "{db_id}" [{error}]')

    def test_connection(self):
        self.acessa_fdb_db('f1')
        pprint(self.test_context)

    def test_output(self):
        self.connect_fdb('f1')
        self.set_cursor()
        
        sql = """
            select
            pc.*
            from SCC_PLANOCONTASNOVO pc
        """
        self.execute(sql)
        print(
            ''.join([
                field[fdb.DESCRIPTION_NAME].ljust(field[fdb.DESCRIPTION_DISPLAY_SIZE])
                for field in self.cursor.description
            ])
        )

        data = self.fetchall()
        pprint(data[:2])

        self.execute(sql)
        data = self.itermap()
        for row in data:
            pprint(dict(row))
            break

        self.execute(sql)
        data = self.cursor.fetchallmap()
        pprint(data[:2])

        # self.executemany(
        #     "insert into languages (name, year_released) values (?, ?)",
        #     [
        #         ('Lisp',  1958),
        #         ('Dylan', 1995),
        #     ],
        # )

        self.close()


if __name__ == '__main__':
    main = Main()
    main.test_connection()
    main.test_output()
