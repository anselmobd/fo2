#!/usr/bin/env python

from pprint import pprint
import locale
import argparse


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

    def processa(self):
        pass


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
    inv.processa()
