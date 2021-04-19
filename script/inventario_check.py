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
        self.abre_inventario()

    def abre_inventario(self):
        try:
            with open(self._inventario) as csvfile:
                self._inventario_reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                self.abre_compras()
        except Exception:
            print(f"Não consegui abrir para leitura {self._inventario}")
            sys.exit(10)

    def abre_compras(self):
        try:
            with open(self._compras) as csvfile:
                self._compras_reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                self.abre_saida()
        except Exception:
            print(f"Não consegui abrir para leitura {self._compras}")
            sys.exit(11)

    def abre_saida(self):
        try:
            with open(self._saida) as csvfile:
                self._saida_writer = csv.writer(csvfile, delimiter=';', quotechar='"')
                self.processa()
        except Exception:
            print(f"Não consegui abrir para escrita {self._saida}")
            sys.exit(11)

    def processa(self):
        for inv in self._inventario_reader:
            pprint(inv)


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
