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
        self.abre_arquivos()
        self.processa()

    def abre_arquivos(self):
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

    def abre_inventario(self):
        try:
            self._inventario_csvfile = open(self._inventario, newline='')
            self._inventario_reader = csv.DictReader(
                self._inventario_csvfile, delimiter=';', quotechar='"')
        except Exception as e:
            print(f"Não consegui abrir para leitura {self._inventario}")
            raise e

    def abre_compras(self):
        try:
            self._compras_csvfile = open(self._compras, newline='')
            self._compras_reader = csv.DictReader(
                self._compras_csvfile, delimiter=';', quotechar='"')
        except Exception as e:
            print(f"Não consegui abrir para leitura {self._compras}")
            raise e

    def abre_saida(self):
        try:
            self._saida_csvfile = open(self._saida, 'w', newline='')
            self._saida_writer = None
        except Exception as e:
            print(f"Não consegui abrir para escrita {self._saida}")
            raise e

    def make_csv_mask(self, values):
        sep = ''
        result = ''
        for val in values:
            if isinstance(val, str):
                result += sep + '"{}"'
            else:
                result += sep + '{}'
            sep = ';'
        return result+"\n"

    def print_row_values(self, values):
        for i in range(len(values)):
            if isinstance(values[i], str):
                values[i] = values[i].strip()
            else:
                values[i] = locale.currency(
                    values[i], grouping=False, symbol=None)
        self._saida_csvfile.write(self._mask.format(*values))

    def processa(self):
        compras = [
            {k: v for k, v in row.items()}
            for row in self._compras_reader
        ]
        # pprint(compras[:2])
        self._mask = None
        self._print_header = True

        for inv in self._inventario_reader:
            inv_line = dict(inv.items())
            inv_line['Quantidade'] = locale.atof(inv_line['Quantidade'])
            inv_line['Valor unitário'] = locale.atof(inv_line['Valor unitário'])
            inv_line['Valor total'] = locale.atof(inv_line['Valor total'])
            inv_line['Conta contábil'] = locale.atof(inv_line['Conta contábil'])

            keys = list(inv_line.keys())

            nivel, ref, tam, cor = tuple(inv_line['Código'].split('.'))
            compra_line = next(
                (
                    item 
                    for item in compras
                    if (
                        item["Nível"] == nivel
                        and item["Referência"] == ref
                        and item["Tamanho"] == tam
                        and item["Cor"] == cor
                    )
                ),
                None
            )

            if compra_line:
                qtd_inv = inv_line['Quantidade']
                qtd_compra = locale.atof(compra_line['Quantidade'])
                qtd_dif = abs(qtd_inv - qtd_compra)
                if (
                    min(qtd_dif, qtd_inv, 100) == 100
                    and qtd_dif > qtd_inv * 0.5
                ):
                    print(f"{inv_line['Código']} alterado")
                    inv_line['Quantidade'] = qtd_compra
                    inv_line['Valor total'] = inv_line['Valor unitário'] * inv_line['Quantidade']

            values = list(inv_line.values())

            # if not self._saida_writer:
            #     self._saida_writer = csv.DictWriter(
            #         self._saida_csvfile, inv_line.keys(), delimiter=';', quotechar='"',
            #         quoting=csv.QUOTE_NONNUMERIC,
            #     )
            #     self._saida_writer.writeheader()
            # self._saida_writer.writerow(inv_line)

            if not self._mask:
                self._mask = self.make_csv_mask(values)

            if self._print_header:
                self._print_header = False
                self._saida_csvfile.write(';'.join(keys)+"\n")

            self.print_row_values(values)


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
