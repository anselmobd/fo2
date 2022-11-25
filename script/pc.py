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


class PG():

    def __init__(self, *args, **kwargs):
        super(PG, self).__init__(*args, **kwargs)
        self.con = self.connect('persona')
        self.cur = self.con.cursor()

    def connect(self, id):
        db = _DATABASES[id]
        return psycopg2.connect(
            host=db['HOST'],
            port=db['PORT'],
            database=db['NAME'],
            user=db['USER'],
            password=db['PASSWORD'],
        )


class Main():

    def __init__(self, fb, pg, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)
        self.fb = fb
        self.pg = pg
        self.test_context = {
            'msgs_ok': [],
            'msgs_erro': [],
        }

    def close(self):
        self.fb.con.close()
        self.pg.con.close()

    def fb_print_nivel1(self):
        data = self.fb_get_pc(nivel=1)

        for row in data:
            row['conta'] = row['conta'].rstrip('.0')
            row['descricao'] = tira_acento_upper(row['descricao'])
            print("{conta};{descricao}".format(**row))

    def pg_insert_ca(self, plano_auxiliar=None, nivel=1, codigo=None):
        if not (plano_auxiliar and codigo):
            return
        if self.pg_get_caa(plano_auxiliar, codigo=codigo):
            return False
        len_mae = {
            1: 0,
            2: 1,
            3: 2,
        }
        codigo_mae = codigo[:len_mae[nivel]]
        sql = f"""
            insert into contabil.contasauxiliares (
                planoauxiliar
            , contamae
            , codigo
            , tenant
            )
            select 
                p.planoauxiliar 
            , ca.contaauxiliar contamae
            , '{codigo}' codigo
            , p.tenant
            from contabil.planosauxiliares p
            left join contabil.contasauxiliares ca
                on ca.planoauxiliar = p.planoauxiliar 
                and ca.codigo = '{codigo_mae}'
            where p.codigo = '{plano_auxiliar}'
        """
        self.pg.cur.execute(sql)
        self.pg.con.commit()
        return True

    def fb_get_pc(self, nivel=2, maior_que=None):
        filtro_nivel = {
            1: "and pc.conta like '%.0.00'" ,
            2: """--
                and pc.conta not like '%.0.00'
                and pc.conta like '%.00'
            """,
        }
        filtro_maior_que = (
            f"and pc.conta > '{maior_que}'"
            if maior_que else ''
        )
        sql = f"""
            select
              pc.*
            from SCC_PLANOCONTASNOVO pc
            where 1=1
              and pc.conta not like '0%'
              {filtro_nivel[nivel]} -- filtro_nivel
              {filtro_maior_que} -- filtro_maior_que
            order by
              pc.conta
        """
        self.fb.cur.execute(sql)
        data = dictlist_lower(self.fb.cur)

        for row in data:
            row['conta'] = row['conta'].rstrip('.0').replace('.', '')
            row['descricao'] = tira_acento_upper(row['descricao'])
        return data

    def pg_select_to_insert_caa(
            self, plano_auxiliar, ano, codigo, nome):
        return f"""
            select 
              {ano} ano
            , '{nome}' nome
            , ca.contaauxiliar
            , ca.tenant 
            , (
                select 
                  TO_CHAR((max(caa2.reduzido)::integer + 1), 'fm000000')
                from contabil.planosauxiliares p2
                join contabil.contasauxiliares ca2
                  on ca2.planoauxiliar = p2.planoauxiliar 
                join contabil.contasauxiliaresanuais caa2
                  on caa2.contaauxiliar = ca2.contaauxiliar 
                where p2.planoauxiliar = p.planoauxiliar
                  and caa2.ano = {ano}
              ) reduzido
            from contabil.planosauxiliares p
            join contabil.contasauxiliares ca
              on ca.planoauxiliar = p.planoauxiliar 
            where p.codigo = '{plano_auxiliar}'
              and ca.codigo = '{codigo}'
        """

    def pg_print_to_insert_caa(
            self, plano_auxiliar, ano, codigo, nome):
        sql = self.pg_select_to_insert_caa(
            plano_auxiliar, ano, codigo, nome)
        self.pg.cur.execute(sql)
        data = dictlist_lower(self.pg.cur)
        pprint(data)

    def pg_insert_caa_nivel1(
            self, plano_auxiliar, ano, codigo, nome):
        verifica = self.pg_get_caa(plano_auxiliar, ano, codigo)
        if verifica and verifica[0]['nome']:
            return False
        sql = f"""
            insert into contabil.contasauxiliaresanuais (
              ano
            , nome
            , contaauxiliar
            , tenant
            , reduzido
            )
        """ + self.pg_select_to_insert_caa(
            plano_auxiliar, ano, codigo, nome)
        self.pg.cur.execute(sql)
        self.pg.con.commit()
        return True

    def pg_get_caa(self, plano_auxiliar, ano=0, codigo=None):
        filtra_codigo = (
            f"AND ca.codigo = '{codigo}'"
            if codigo else ''
        )
        sql = f"""
            select 
              ca.codigo 
            , caa.*
            from contabil.planosauxiliares p
            join contabil.contasauxiliares ca
              on ca.planoauxiliar = p.planoauxiliar 
            left join contabil.contasauxiliaresanuais caa
              on caa.contaauxiliar = ca.contaauxiliar 
              and caa.ano = {ano}
            where p.codigo = '{plano_auxiliar}'
              {filtra_codigo} -- filtra_codigo
            order by
              ca.codigo
        """
        self.pg.cur.execute(sql)
        data = dictlist_lower(self.pg.cur)
        return data

    def pg_print_caa(self, plano_auxiliar, ano, codigo=None):
        data = self.pg_get_caa(plano_auxiliar, ano, codigo=codigo)
        if data:
            for row in data:
                print(row['codigo'].ljust(4), row['nome'])
        else:
            print(codigo.ljust(4), "[]")

    def insere_nivel1(self, plano_auxiliar, ano):
        self.pg_print_caa(plano_auxiliar, ano)

        dados = self.fb_get_pc(nivel=1)
        for row in dados:
            self.pg_insert_ca(plano_auxiliar, codigo=row['conta'])
            self.pg_print_to_insert_caa(
                plano_auxiliar, ano, row['conta'], row['descricao'])
            self.pg_insert_caa_nivel1(
                plano_auxiliar, ano, row['conta'], row['descricao'])

        self.pg_print_caa(plano_auxiliar, ano)

    def insere_nivel2(self, plano_auxiliar, ano):
        dados = self.fb_get_pc(nivel=2)
        for row in dados:
            self.pg_print_caa(plano_auxiliar, ano, row['conta'])
            inseriu = self.pg_insert_ca(
                plano_auxiliar, nivel=2, codigo=row['conta'])
            if inseriu:
                self.pg_print_caa(plano_auxiliar, ano, row['conta'])
            inseriu = self.pg_insert_caa_nivel1(
                plano_auxiliar, ano, row['conta'], row['descricao'])
            if inseriu:
                self.pg_print_caa(plano_auxiliar, ano, row['conta'])


if __name__ == '__main__':

    fb = FB()
    pg = PG()

    main = Main(fb=fb, pg=pg)

    # main.fb_print_nivel1()
    # main.pg_print_caa('SCC ANSELMO', 2022, '1')
    # main.pg_print_caa('SCC ANSELMO', 2022)

    # main.insere_nivel1('SCC ANSELMO', 2022)
    main.insere_nivel2('SCC ANSELMO', 2022)

    main.close()
