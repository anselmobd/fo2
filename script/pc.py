#!/usr/bin/env python3

import fdb
import psycopg2
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

def no_accent(texto):
    process = unicodedata.normalize("NFD", texto)
    process = process.encode("ascii", "ignore")
    return process.decode("utf-8")

def no_accent_up(texto):
    return no_accent(texto).upper()


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

    def close_dbs(self):
        self.fb.con.close()
        self.pg.con.close()

    def fb_print_pc(self, nivel=0):
        data = self.fb_get_pc(nivel=nivel)
        for row in data:
            print("{conta};{descricao}".format(**row))

    def fb_print_cc(self, nivel=0):
        data = self.fb_get_cc(nivel=nivel)
        for row in data:
            print("{estrutura};{descricao}".format(**row))

    def pg_insert_pc_codigo(self, nome_pc=None, ano=0, nivel=1, codigo=None):
        if not (nome_pc and codigo):
            return
        if self.pg_get_pc(nome_pc, ano=ano, codigo=codigo):
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
            where p.codigo = '{nome_pc}'
        """
        self.pg.cur.execute(sql)
        self.pg.con.commit()
        return True

    def pg_insert_cc_codigo(self, empresa=None, ano=0, nivel=1, codigo=None):
        if not (empresa and codigo):
            return
        if self.pg_get_cc(empresa, ano=ano, codigo=codigo):
            return False
        codigo_mae=".".join(codigo.split(".")[:-1])
        sql = f"""
            insert into contabil.centrosdecusto (
              empresa 
            , centrodecustomae 
            , codigo
            , tenant
            )
            select 
              e.empresa 
            , cc.centrodecusto centrodecustomae
            , '{codigo}' codigo
            , ( select 
                  max(t.tenant)
                from ns.tenants t  
              ) tenant
            from ns.empresas e
            left join contabil.centrosdecusto cc
              on cc.empresa = e.empresa 
             and cc.codigo = '{codigo_mae}'
            where e.codigo = '{empresa}'
        """
        self.pg.cur.execute(sql)
        self.pg.con.commit()
        return True

    def parte_significativa(self, codigo):
        estr_partes = codigo.split(".")
        while estr_partes and int(estr_partes[-1]) == 0:
            del(estr_partes[-1])
        return estr_partes

    def valores_filtro_nivel(self, nivel, mascara="0.0.00"):
        partes = mascara.split(".")
        if nivel < 1 or nivel > len(partes):
            return None, None
        partes_filtro = partes[nivel-1:]
        not_like = ".".join(partes_filtro)
        not_like = f"%.{not_like}"[-len(mascara):]
        partes_filtro[0] = "%"
        is_like = ".".join(partes_filtro)
        return not_like, is_like

    def fb_get_pc(self, nivel=0, maior_que=None):
        not_like, is_like = self.valores_filtro_nivel(nivel)
        filtro_maior_que = (
            f"and pc.conta > '{maior_que}'"
            if maior_que else ''
        )
        sql = f"""
            select
              pc.*
            from SCC_PLANOCONTASNOVO pc
            where 1=1
              and pc.conta not like '{not_like}'
              and pc.conta like '{is_like}'
              {filtro_maior_que} -- filtro_maior_que
            order by
              pc.conta
        """
        self.fb.cur.execute(sql)
        data = dictlist_lower(self.fb.cur)

        for row in data:
            row['conta'] = ''.join(self.parte_significativa(row['conta']))
            row['descricao'] = no_accent_up(row['descricao'])
        return data

    def fb_get_cc(self, nivel=0):
        not_like, is_like = self.valores_filtro_nivel(
            nivel, mascara="0.0.00.00")
        sql = f"""
            select
              cc.*
            from SCC_CENTROCUSTO cc
            where 1=1
              and cc.estrutura not like '{not_like}'
              and cc.estrutura like '{is_like}'
            order by
              cc.estrutura
        """
        self.fb.cur.execute(sql)
        data = dictlist_lower(self.fb.cur)

        for row in data:
            row['estrutura'] = '.'.join(self.parte_significativa(row['estrutura']))
            row['descricao'] = no_accent_up(row['descricao'])
        return data

    def pg_select_to_insert_pc_nome(
            self, nome_pc, ano, codigo, nome):
        return f"""
            select 
              {ano} ano
            , '{nome}' nome
            , ca.contaauxiliar
            , ca.tenant 
            , coalesce(( select 
                  TO_CHAR((max(caa2.reduzido)::integer + 1), 'fm000000')
                from contabil.planosauxiliares p2
                join contabil.contasauxiliares ca2
                  on ca2.planoauxiliar = p2.planoauxiliar 
                join contabil.contasauxiliaresanuais caa2
                  on caa2.contaauxiliar = ca2.contaauxiliar 
                where p2.planoauxiliar = p.planoauxiliar
                  and caa2.ano = {ano}
              ), '000001') reduzido
            from contabil.planosauxiliares p
            join contabil.contasauxiliares ca
              on ca.planoauxiliar = p.planoauxiliar 
            where p.codigo = '{nome_pc}'
              and ca.codigo = '{codigo}'
        """

    def pg_print_to_insert_pc_nome(
            self, nome_pc, ano, codigo, nome):
        sql = self.pg_select_to_insert_pc_nome(
            nome_pc, ano, codigo, nome)
        self.pg.cur.execute(sql)
        data = dictlist_lower(self.pg.cur)
        pprint(data)

    def pg_insert_pc_nome(
            self, nome_pc, ano, codigo, nome):
        verifica = self.pg_get_pc(nome_pc, ano, codigo)
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
        """ + self.pg_select_to_insert_pc_nome(
            nome_pc, ano, codigo, nome)
        self.pg.cur.execute(sql)
        self.pg.con.commit()
        return True

    def pg_get_pc(self, nome_pc, ano, codigo=None):
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
            where p.codigo = '{nome_pc}'
              {filtra_codigo} -- filtra_codigo
            order by
              ca.codigo
        """
        self.pg.cur.execute(sql)
        data = dictlist_lower(self.pg.cur)
        return data

    def pg_print_pc(self, nome_pc, ano, codigo=None):
        data = self.pg_get_pc(nome_pc, ano, codigo=codigo)
        if data:
            for row in data:
                print(row['codigo'].ljust(4), row['nome'])
        else:
            print(codigo.ljust(4), "[]")

    def pg_select_to_insert_cc_nome(
            self, empresa, ano, codigo, nome):
        return f"""
            select 
              {ano} ano
            , '{nome}' nome
            , 0 natureza
            , cc.centrodecusto
            , cc.tenant 
            from ns.empresas e
            join contabil.centrosdecusto cc
              on cc.empresa = e.empresa 
            where e.codigo = '{empresa}'
              AND cc.codigo = '{codigo}'
        """

    def pg_print_to_insert_cc_nome(
            self, empresa, ano, codigo, nome):
        sql = self.pg_select_to_insert_cc_nome(
            empresa, ano, codigo, nome)
        self.pg.cur.execute(sql)
        data = dictlist_lower(self.pg.cur)
        pprint(data)

    def pg_insert_cc_nome(
            self, empresa, ano, codigo, nome):
        verifica = self.pg_get_cc(empresa, ano, codigo)
        if verifica and verifica[0]['nome']:
            return False
        sql = f"""
            insert into contabil.centrosdecustoanuais (
              ano
            , nome
            , natureza 
            , centrodecusto
            , tenant
            )
        """ + self.pg_select_to_insert_cc_nome(
            empresa, ano, codigo, nome)
        self.pg.cur.execute(sql)
        self.pg.con.commit()
        return True

    def pg_get_cc(self, empresa, ano=0, codigo=None):
        filtra_codigo = (
            f"AND cc.codigo = '{codigo}'"
            if codigo else ''
        )
        sql = f"""
            select 
              cc.codigo
            , cca.*
            from ns.empresas e
            join contabil.centrosdecusto cc
              on cc.empresa = e.empresa 
            left join contabil.centrosdecustoanuais cca
              on cca.centrodecusto = cc.centrodecusto 
             and cca.ano = {ano}
            where e.codigo = '{empresa}'
              {filtra_codigo} -- filtra_codigo
            order by
              cc.codigo
        """
        self.pg.cur.execute(sql)
        data = dictlist_lower(self.pg.cur)
        return data

    def pg_print_cc(self, empresa, ano, codigo=None):
        data = self.pg_get_cc(empresa, ano, codigo=codigo)
        if data:
            for row in data:
                print(row['codigo'].ljust(9), row['nome'])
        else:
            print(codigo.ljust(9), "[]")

    def pg_insert_pc(self, nome_pc, ano):
        for nivel in range(1, 4):
            self.pg_insert_pc_nivel(
                nome_pc=nome_pc, nivel=nivel, ano=ano)

    def pg_insert_pc_nivel(self, nome_pc, nivel=1, ano=0):
        dados = self.fb_get_pc(nivel=nivel)
        for row in dados:
            self.pg_print_pc(nome_pc, ano, row['conta'])
            inseriu = self.pg_insert_pc_codigo(
                nome_pc, ano=ano, nivel=nivel, codigo=row['conta'])
            if inseriu:
                self.pg_print_pc(nome_pc, ano, row['conta'])
            inseriu = self.pg_insert_pc_nome(
                nome_pc, ano, row['conta'], row['descricao'])
            if inseriu:
                self.pg_print_pc(nome_pc, ano, row['conta'])

    def pg_insert_cc(self, empresa, ano):
        for nivel in range(1, 5):
            self.pg_insert_cc_nivel(
                empresa=empresa, nivel=nivel, ano=ano)

    def pg_insert_cc_nivel(self, empresa, nivel=1, ano=0):
        dados = self.fb_get_cc(nivel=nivel)
        for row in dados:
            self.pg_print_cc(empresa, ano, row['estrutura'])
            inseriu = self.pg_insert_cc_codigo(
                empresa, ano=ano, nivel=nivel, codigo=row['estrutura'])
            if inseriu:
                self.pg_print_cc(empresa, ano, row['estrutura'])
                # raise SystemExit
            inseriu = self.pg_insert_cc_nome(
                empresa, ano, row['estrutura'], row['descricao'])
            if inseriu:
                self.pg_print_cc(empresa, ano, row['estrutura'])
                # raise SystemExit


if __name__ == '__main__':

    fb = FB()
    pg = PG()

    main = Main(fb=fb, pg=pg)

    # main.fb_print_pc(nivel=2)
    # main.fb_print_cc(nivel=3)
    # main.pg_print_pc('F1SCC', 2022, '1')
    # main.pg_print_pc('F1SCC', 2022)
    # main.pg_print_cc('DUOMO', 2022, '2')
    # main.pg_print_cc('DUOMO', 2022)

    # main.pg_insert_pc_nivel('F1SCC', nivel=1, ano=2022)
    # main.pg_insert_pc_nivel('F1SCC', nivel=2, ano=2022)
    # main.pg_insert_pc_nivel('F1SCC', nivel=3, ano=2022)
    # main.pg_insert_pc('F1SCC', ano=2022)

    main.pg_insert_cc('DUOMO', ano=2022)

    # pprint(main.valores_filtro_nivel(1))
    # pprint(main.valores_filtro_nivel(2))
    # pprint(main.valores_filtro_nivel(3))

    main.close_dbs()
