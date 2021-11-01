#!/usr/bin/env python

import csv
import pandas as pd
import psycopg2
import sys
import timeit
from collections import namedtuple
from pprint import pprint

from db_password import (
    DBPASS,
)


def rows_to_dict_list_lower(cursor):
    columns = [i[0].lower() for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def rows_to_namedtuple(cursor):
    Row = namedtuple('Row', [i[0].lower() for i in cursor.description])
    return [Row(*row) for row in cursor]


class ExpCD():

    _RUAS = {
        'A': 'AB',
        'B': 'AB',
        'C': 'CD',
        'D': 'CD',
        'E': 'EF',
        'F': 'EF',
        'G': 'GH',
        'H': 'GH',
    }

    def conecta(self):
        self.conn = psycopg2.connect(
            host="localhost",
            port=25432,
            database="tussor_fo2_production",
            user="tussor_fo2",
            password=DBPASS,
        )
        self.cursor = self.conn.cursor()
    
    def get_locais_sql(self):
        return """
            select distinct
              l.local
            , '' rota
            from fo2_cd_lote l
            left join fo2_cd_endereco_disponivel ed 
              on ed.disponivel
             and l.local like (ed.inicio || '%')
            left join fo2_cd_endereco_disponivel ned 
              on ed.disponivel is not null
             and (not ned.disponivel)
             and ned.inicio like (ed.inicio || '%')
             and l.local like (ned.inicio || '%')
            where l.local is not null
              and l.local <> ''
              and ed.disponivel is not null
              and ned.disponivel is null
            order by
              l.local
        """

    def get_locais_lotes_sql(self):
        return """
            select
              l.local
            , substring(l.lote, 1, 4) periodo
            , substring(l.lote, 5, 5) oc
            from fo2_cd_lote l
            left join fo2_cd_endereco_disponivel ed 
              on ed.disponivel
             and l.local like (ed.inicio || '%')
            left join fo2_cd_endereco_disponivel ned 
              on ed.disponivel is not null
             and (not ned.disponivel)
             and ned.inicio like (ed.inicio || '%')
             and l.local like (ned.inicio || '%')
            where l.local is not null
              and l.local <> ''
              and ed.disponivel is not null
              and ned.disponivel is null
            group by 
              l.local
            , l.lote
            order by
              l.local
            , l.lote
        """

    def get_solicitacoes_pedidos_sql(self):
        return """
            with solic_todas as
            ( select
                s.id
              , s.codigo
              , s.descricao
              , s.data
              , s.ativa
              , s.create_at
              , s.update_at
              , s.usuario_id
              , s.concluida
              , s.can_print
              , s.coleta
              , u.username usuario__username
              , coalesce(sum(sq.qtd), 0) total_qtd
              , coalesce(sum(
                  case when l.local is null
                  then 0
                  else sq.qtd
                  end
                ), 0) total_no_cd
              , ( select 
                    count(*)
                  from fo2_cd_solicita_lote_pedido slp
                  where slp.solicitacao_id = s.id
                ) as n_pedidos
              from fo2_cd_solicita_lote s
              left join fo2_cd_solicita_lote_qtd sq
                on sq.solicitacao_id = s.id
               and sq.origin_id = 0
              left join fo2_cd_lote l
                on l.id = sq.lote_id
              left join auth_user u
                on u.id = s.usuario_id
              where 1=1
              group by
                s.id
              , s.codigo
              , s.descricao
              , s.ativa
              , s.create_at
              , s.update_at
              , s.usuario_id
              , u.username
              order by
                s.update_at desc
            )
            select
              s.id num_solic
            --, s.codigo
            --, s.descricao
            , slp.pedido 
            from solic_todas s
            join fo2_cd_solicita_lote_pedido slp
              on slp.solicitacao_id = s.id
            where 1=1
              and s.total_no_cd <> 0
              and s.n_pedidos <> 0
            order by
              s.id
            , slp.pedido 
        """

    def get_locais(self):
        self.cursor.execute(self.get_locais_sql())

    def print_cursor_fetchall(self):
        self.get_locais()
        data = self.cursor.fetchall()
        pprint(data[:10])
        print(data[0][0])
        print('fetchall', sys.getsizeof(data))

    def print_cursor_dict(self):
        self.get_locais()
        data = rows_to_dict_list_lower(self.cursor)
        pprint(data[:10])
        print(data[0]['local'])
        print('dict', sys.getsizeof(data))

    def print_cursor_namedtuple(self):
        self.get_locais()
        data = rows_to_namedtuple(self.cursor)
        pprint(data[:10])
        print(data[0].local)
        print('namedtuple', sys.getsizeof(data))

    def print_cursor_pd(self):
        data = pd.read_sql_query(
            self.get_locais_sql(), self.conn
        )
        pprint(data[:10])
        pprint(data[0:1])
        print('pd', sys.getsizeof(data))

    def convert_local(self, row):
        if 'local' in row._fields:
            bloco = row.local[0]
            andar = row.local[1]
            ap = row.local[2:]
            if bloco <= 'H':
                espaco = '1'
                andar = f'0{andar}'
            else:
                espaco = '2'
            if bloco == 'D':
                iap = int(ap)
                if iap > 18:
                    iap += 4
                elif iap > 11:
                    iap += 3
                elif iap > 5:
                    iap += 1
                ap = f'{iap:02}'
            row = row._replace(local=f'{espaco}{bloco}{andar}{ap}')
        return row

    def calc_rota(self, row):
        if 'local' in row._fields:
            espaco = row.local[0]
            bloco = row.local[1]
            ap = row.local[4:]
            if bloco <= 'H':
                iap = int(ap)
                irota = iap//2
                rua = self._RUAS[bloco]
                rota = f'{espaco}{rua}{irota:02}'
            else:
                rota = f'{espaco}{bloco}'
            row = row._replace(rota=rota)
        return row


    def export_locais(self):
        self.get_locais()
        data = rows_to_namedtuple(self.cursor)
        if data:
            with open('locais.csv', 'w') as csvfile:
                csvwriter = csv.writer(
                    csvfile,
                    delimiter=';',
                )
                csvwriter.writerow(data[0]._fields)
                for row in data:
                    csvwriter.writerow(self.calc_rota(self.convert_local(row)))

    def export_locais_lotes(self):
        self.cursor.execute(self.get_locais_lotes_sql())
        data = rows_to_namedtuple(self.cursor)
        if data:
            with open('locais_lotes.csv', 'w') as csvfile:
                csvwriter = csv.writer(
                    csvfile,
                    delimiter=';',
                )
                csvwriter.writerow(data[0]._fields)
                for row in data:
                    csvwriter.writerow(self.convert_local(row))

    def export_solicitacoes_pedidos(self):
        self.cursor.execute(self.get_solicitacoes_pedidos_sql())
        data = rows_to_namedtuple(self.cursor)
        if data:
            with open('solicitacoes_pedidos.csv', 'w') as csvfile:
                csvwriter = csv.writer(
                    csvfile,
                    delimiter=';',
                )
                csvwriter.writerow(data[0]._fields)
                for row in data:
                    csvwriter.writerow(row)


def get_timeit(func):
    starttime = timeit.default_timer()
    func()
    print("Timeit:", timeit.default_timer() - starttime)


def main():
    ecd = ExpCD()
    ecd.conecta()

    # get_timeit(ecd.print_cursor_fetchall)
    # get_timeit(ecd.print_cursor_dict)
    # get_timeit(ecd.print_cursor_namedtuple)
    # get_timeit(ecd.print_cursor_pd)

    ecd.export_locais()
    ecd.export_locais_lotes()
    ecd.export_solicitacoes_pedidos()


if __name__ == '__main__':
    main()
