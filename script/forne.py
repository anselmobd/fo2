#!/usr/bin/env python3

import csv
import cx_Oracle
import glob
import sys
import xml.etree.ElementTree as ET
from pprint import pprint


_NS = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}


class Oracle:

    def __init__(self,
        username='systextil',
        password='oracle',
        hostname='localhost',
        # port=28521,
        # servicename='XE',
        port=14521,
        servicename='db_pdb1.sub02011943440.tussorvcn.oraclevcn.com',
        schema='SYSTEXTIL',
    ):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.port = port
        self.servicename = servicename
        self.schema = schema

    def connect(self):
        try:
            self.con = cx_Oracle.connect(
                self.username,
                self.password,
                '{}:{}/{}'.format(
                    self.hostname,
                    self.port,
                    self.servicename
                )
            )
        except cx_Oracle.DatabaseError as e:
            print('[Connection error] {}'.format(e))
            sys.exit(1)

        self.con.current_schema = self.schema
        self.cursor = self.con.cursor()

        try:
            self.cursor.execute(
                'select USERNAME from SYS.ALL_USERS')
        except cx_Oracle.DatabaseError as e:
            print('[Schema {} error] {}'.format(self.schema, e))
            sys.exit(2)

    def execute(self, sql, **xargs):
        try:
            if len(xargs.keys()) == 0:
                self.cursor.execute(sql)
            else:
                self.cursor.execute(sql, xargs)
        except cx_Oracle.DatabaseError as e:
            print('[Execute error] {}'.format(e))
            sys.exit(3)

        result = {
            'keys': [f[0] for f in self.cursor.description],
            'data': self.cursor.fetchall(),
        }
        return result

    def close(self):
        try:
            if self.con:
                if self.cursor is not None:
                    self.cursor.close()
                self.con.close()
        except cx_Oracle.DatabaseError as e:
            print('[Closing error] {}'.format(e))
            sys.exit(4)

    def get_emails(self, cnpj):
        sql = f"""
            SELECT
              f.E_MAIL
            , f.NFE_E_MAIL
            FROM SUPR_010 f -- fornecedor
            WHERE f.FORNECEDOR9 = {cnpj[:8]}
              AND f.FORNECEDOR4 = {cnpj[8:12]}
              AND f.FORNECEDOR2 = {cnpj[12:]}
        """
        # print(sql)
        data = list(self.cursor.execute(sql))
        if data:
            emails = data[0]
            return map(lambda e: e or '', emails)
        return "", ""


def get_in(level, node):
    return level.findall(f'nfe:{node}', _NS)


def get0_in(level, node):
    try:
        return get_in(level, node)[0]
    except Exception:  # IndexError ET.ParseError
        return None


def get0text_in(level, node):
    elem = get0_in(level, node)
    return '' if elem is None else elem.text


def parse_nfe(file, fornecedores, db):
    # print(file)
    try:
        tree = ET.parse(file)
        # print(tree)
    except Exception:
        return

    try:
        root = tree.getroot()
        # print(root)
    except Exception:
        return
    
    NFe = get0_in(root, 'NFe')
    # print(NFe)
    if NFe is None:
        return

    infNFe = get0_in(NFe, 'infNFe')
    # print(infNFe)
    if infNFe is None:
        return

    emit = get0_in(infNFe, 'emit')
    # print(emit)
    if emit is None:
        return

    CNPJ = get0text_in(emit, 'CNPJ')
    # print(CNPJ)
    # print(CNPJ.text)

    if CNPJ not in fornecedores:
        xNome = get0text_in(emit, 'xNome')
        # print(xNome)
        # print(xNome.text)
        xFant = get0text_in(emit, 'xFant')
        IE = get0text_in(emit, 'IE')

        enderEmit = get0_in(emit, 'enderEmit')
        xLgr = get0text_in(enderEmit, 'xLgr')
        nro = get0text_in(enderEmit, 'nro')
        xBairro = get0text_in(enderEmit, 'xBairro')
        xMun = get0text_in(enderEmit, 'xMun')
        UF = get0text_in(enderEmit, 'UF')
        CEP = get0text_in(enderEmit, 'CEP')
        fone = get0text_in(enderEmit, 'fone')

        email, nfe_email = db.get_emails(CNPJ)

        fornecedores[CNPJ] = {
            'xNome': xNome,
            'xFant': xFant,
            'IE': IE,
            'xLgr': xLgr,
            'nro': nro,
            'xBairro': xBairro,
            'xMun': xMun,
            'UF': UF,
            'CEP': CEP,
            'fone': fone,
            'email': email,
            'nfe_email': nfe_email,
        }


def to_csv(forns):
    with open('forne.csv', 'w', newline='') as csvfile:
        cwriter = csv.writer(
            csvfile,
            dialect='unix',
            delimiter=';',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL
        )
        cwriter.writerow([
            'cnpj',
            'xNome',
            'xFant',
            'IE',
            'xLgr',
            'nro',
            'xBairro',
            'xMun',
            'UF',
            'CEP',
            'fone',
            'email',
            'nfe_email',
        ])
        for cnpj in forns:
            cwriter.writerow([
                cnpj,
                forns[cnpj]['xNome'],
                forns[cnpj]['xFant'],
                forns[cnpj]['IE'],
                forns[cnpj]['xLgr'],
                forns[cnpj]['nro'],
                forns[cnpj]['xBairro'],
                forns[cnpj]['xMun'],
                forns[cnpj]['UF'],
                forns[cnpj]['CEP'],
                forns[cnpj]['fone'],
                forns[cnpj]['email'],
                forns[cnpj]['nfe_email'],
            ])


def main():
    files = glob.iglob('./*.xml')

    db = Oracle()
    db.connect()

    fornecedores = {}
    for file in files:
        parse_nfe(file, fornecedores, db)

    pprint(fornecedores)

    to_csv(fornecedores)


if __name__ == '__main__':
    main()
