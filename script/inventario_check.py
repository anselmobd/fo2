#!/usr/bin/env python

import argparse
import csv
import locale
import sys
from pprint import pprint


class Corrige:

    def __init__(self):
        # parametros - valor default (ou None)
        self._inventario = None
        self._compras = None
        self._saida = None

    @property
    def inventario(self):
        return self._inventario

    @inventario.setter
    def inventario(self, value):
        self._inventario = value

    @property
    def compras(self):
        return self._compras

    @compras.setter
    def compras(self, value):
        self._compras = value

    @property
    def saida(self):
        return self._saida

    @saida.setter
    def saida(self, value):
        self._saida = value

    def executa(self):
        try:
            self.abre_inventario()
            self.abre_compras()
            self.abre_saida()
        except Exception as e:
            try:
                self._inventario_csvfile.close()
            except Exception:
                pass
            try:
                self._compras_csvfile.close()
            except Exception:
                pass
            try:
                self._saida_csvfile.close()
            except Exception:
                pass
            raise e
        self.processa()

    def abre_inventario(self):
        try:
            self._inventario_csvfile = open(self._inventario, newline='')
            self._inventario_reader = csv.reader(
                self._inventario_csvfile, delimiter=';', quotechar='"')
        except Exception as e:
            print(f"Não consegui abrir para leitura {self._inventario}")
            raise e

    def abre_compras(self):
        try:
            self._compras_csvfile = open(self._compras, newline='')
            self._compras_reader = csv.reader(
                self._compras_csvfile, delimiter=';', quotechar='"')
        except Exception as e:
            print(f"Não consegui abrir para leitura {self._compras}")
            raise e

    def abre_saida(self):
        try:
            self._saida_csvfile = open(self._saida, 'w', newline='')
            self._saida_writer = csv.writer(
                self._saida_csvfile, delimiter=';', quotechar='"')
        except Exception as e:
            print(f"Não consegui abrir para escrita {self._saida}")
            raise e

    def processa(self):
        # compras = {rows[0]:rows[1] for rows in self._compras_reader}
        # pprint(compras)

        for i, inv in enumerate(self._inventario_reader):
            pprint(inv)
            if i > 3:
                break


def parse_args():
    parser = argparse.ArgumentParser(
        description='Corrige valores do arquivo gerado por inventario.py, '
            'baseado nos valores de planilhas do setor de compras',
        epilog="(c) Tussor & Oxigenai",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "inventario",
        help='Arquivo de inventário')
    parser.add_argument(
        "compras",
        help='Arquivo do setor de compras')
    parser.add_argument(
        "saida",
        help='Arquivo corrigido')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    inv = Corrige()
    inv.inventario = args.inventario
    inv.compras = args.compras
    inv.saida = args.saida
    inv.executa()
