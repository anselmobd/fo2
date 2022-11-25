#!/usr/bin/env python3

import csv
import fdb
import psycopg2
import time
import unicodedata 
from pprint import pprint

from db_password import (
    DBPASS_F1,
    DBPASS_PERSONA,
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
    'persona': {  # Nasajon
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "nasajon_db",
        'USER': "postgres",
        'PASSWORD': DBPASS_PERSONA,
        'HOST': 'localhost',
        'PORT': '25433',
    },
}


def dictlist_zip_columns(cursor, columns):
    return [
        dict(zip(columns, row))
        for row in cursor
    ]


def custom_dictlist(cursor, name_case=None):
    if name_case is None:
        columns = [i[0] for i in cursor.description]
    else:
        columns = [name_case(i[0]) for i in cursor.description]
    return dictlist_zip_columns(cursor, columns)


def dictlist(cursor):
    return custom_dictlist(cursor)


def dictlist_lower(cursor):
    return custom_dictlist(cursor, name_case=str.lower)

def tira_acento(texto):
    process = unicodedata.normalize("NFD", texto)
    process = process.encode("ascii", "ignore")
    return process.decode("utf-8")

def tira_acento_upper(texto):
    return tira_acento(texto).upper()


class FB():

    def __init__(self, *args, **kwargs):
        super(FB, self).__init__(*args, **kwargs)
        self.con = self.connect('f1')
        self.cur = self.con.cursor()

    def connect(self, id):
        db = _DATABASES[id]
        return fdb.connect(
            host=db['HOST'],
            port=db['PORT'],
            database=db['NAME'],
            user=db['USER'],
            password=db['PASSWORD'],
            sql_dialect=db['DIALECT'],
            charset=db['OPTIONS']['charset'],
        )

class Main():

    def __init__(self, fb, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)
        self.fb = fb
        self.test_context = {
            'msgs_ok': [],
            'msgs_erro': [],
        }

    def close(self):
        self.fb.con.close()

    def fb_print_nivel1(self):
        data = self.fb_get_pc_nivel1()

        for row in data:
            row['conta'] = row['conta'].rstrip('.0')
            row['descricao'] = tira_acento_upper(row['descricao'])
            print("{conta};{descricao}".format(**row))

        return data

    def connect_pg(self, id):
        db = _DATABASES[id]

        self.pgcon = psycopg2.connect(
            host=db['HOST'],
            port=db['PORT'],
            database=db['NAME'],
            user=db['USER'],
            password=db['PASSWORD'],
        )

    def set_cursor_pg(self):
        self.pgcursor = self.pgcon.cursor()

    def fetch_pg(self, sql):
        self.connect_pg('persona')
        self.set_cursor_pg()

        self.pgcursor.execute(sql)
        # data = self.pgcursor.fetchall()

        data = dictlist_lower(self.pgcursor)

        self.pgcon.close()

        return data

    def testa_pg(self):
        data = self.fetch_pg("""
            select 
            p.codigo
            , p.descricao 
            from contabil.planosauxiliares p
            where p.codigo = 'SCC ANSELMO'
        """)
        pprint(data)

    def exec_pg(self, sql, dados):
        # pprint(sql)
        # pprint(dados)
        self.connect_pg('persona')
        self.set_cursor_pg()

        self.pgcursor.execute(sql, dados)

        self.pgcon.commit()
        self.pgcursor.close()
        self.pgcon.close()

    def testa_insert_pg(self):
        self.exec_pg(
            """
                insert into contabil.contasauxiliares (planoauxiliar, codigo, tenant)
                select 
                  p.planoauxiliar 
                , %s
                , p.tenant  
                from contabil.planosauxiliares p
                where p.codigo = 'SCC ANSELMO'
            """,
            (
                "9",
            ),
        )

    def pg_get_ca(self, codigo=None):
        filtra_codigo = (
            f"AND ca.codigo = '{codigo}'"
            if codigo else ''
        )
        return self.fetch_pg(f"""
            select 
              ca.*
            from contabil.contasauxiliares ca
            where ca.contamae is null
              {filtra_codigo} -- filtra_codigo
        """)

    def pg_print_ca(self):
        data = self.pg_get_ca()
        # pprint(data)
        for row in data:
            print(row['codigo'])

    def pg_insert_ca_nivel1(self, codigo):
        if not self.pg_get_ca(codigo):
            sql = """
                insert into contabil.contasauxiliares
                  (planoauxiliar, codigo, tenant)
                select 
                  p.planoauxiliar 
                , %s
                , p.tenant  
                from contabil.planosauxiliares p
                where p.codigo = 'SCC ANSELMO'
            """
            self.exec_pg(sql, (codigo, ))

    def fb_get_pc_nivel1(self, maior_que=' '):
        sql = f"""
            select
                pc.*
            from SCC_PLANOCONTASNOVO pc
            where pc.conta not like '0%'
                and pc.conta like '%.0.00'
                and pc.conta > '{maior_que}'
            order by
                pc.conta
        """
        self.fb.cur.execute(sql)
        data = dictlist_lower(self.fb.cur)

        for row in data:
            row['conta'] = row['conta'].rstrip('.0')
            row['descricao'] = tira_acento_upper(row['descricao'])
        return data


if __name__ == '__main__':

    fb = FB()

    main = Main(fb=fb)

    dados = main.fb_print_nivel1()

    # main.testa_pg()
    # main.testa_insert_pg()

    ### inserindo nível 1

    main.pg_print_ca()

    dados = main.fb_get_pc_nivel1(maior_que='1.0.00')
    for row in dados:
        main.pg_insert_ca_nivel1(codigo=row['conta'])

    main.pg_print_ca()

    dados = main.fb_get_pc_nivel1(maior_que='6.0.00')
    fb.con.close()
    pprint(dados)

    main.close()
