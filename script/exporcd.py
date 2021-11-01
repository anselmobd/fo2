#!/usr/bin/env python

import pandas as pd
import psycopg2
from pprint import pprint

from db_password import (
    DBPASS,
)


class ExpCD():

    def conecta(self):
        self.conn = psycopg2.connect(
            host="localhost",
            port=25432,
            database="tussor_fo2_production",
            user="tussor_fo2",
            password=DBPASS,
        )
        self.cursor = self.conn.cursor()
    
    def get_locais(self):
        sql = """
            select distinct
              l.local
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
        self.cursor.execute(sql)

    def print_cursor_all(self):
        pprint(self.cursor.fetchall())


def main():
    ecd = ExpCD()
    ecd.conecta()
    ecd.get_locais()
    ecd.print_cursor_all()


if __name__ == '__main__':
    main()
