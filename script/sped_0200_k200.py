#!/usr/bin/env python

import sys
from pprint import pprint
import locale
import argparse
from datetime import datetime, timedelta


class Sped:

    def __init__(self):
        # parametros - valor default (ou None)
        self._ano = None
        self._mes = None

        # outras variaveis utilizadas
        self.blocos = {}

    @property
    def ano(self):
        return self._ano

    @ano.setter
    def ano(self, value):
        if isinstance(value, int):
            self._ano = '{}'.format(value)
        else:
            self._ano = value

    @property
    def mes(self):
        return self._mes

    @mes.setter
    def mes(self, value):
        if isinstance(value, int):
            self._mes = '{:02}'.format(value)
        else:
            self._mes = value

    def import_bloco(self, bloco, arq):
        with open(arq) as data:
            self.blocos[bloco] = data.readlines()

    def bloco0000(self):
        dt_pos_fim = datetime.strptime(
            '01/{mes}/{ano}'.format(mes=self.mes, ano=self.ano),
            '%d/%m/%Y')
        dt_fim = dt_pos_fim-timedelta(days=1)
        dt_fim_str = dt_fim.strftime('%d%m%Y')
        dt_ini = dt_fim-timedelta(days=dt_fim.day-1)
        dt_ini_str = dt_ini.strftime('%d%m%Y')
        self.blocos['0000'] = [
            ('|0000|013|0|{}|{}|TUSSOR CONFECCOES LTDA.|' +
             '07681643000197||RJ|78015110|3304557|03820807||A|0|').format(
                dt_ini_str,
                dt_fim_str,
            )
        ]

    def conta_linhas(self, inic):
        linhas = 0
        for bloco in self.blocos.keys():
            if bloco.startswith(inic):
                linhas += len(self.blocos[bloco])
        return linhas

    def bloco_001(self, nivel):
        self.blocos['{}001'.format(nivel)] = ['|{}001|1|'.format(nivel)]

    def bloco_insere(self, nome):
        self.blocos[nome] = ['|{}|'.format(nome)]

    def bloco_990_calcula(self, nivel):
        self.blocos['{}990'.format(nivel)][0] += \
            '{}|'.format(self.conta_linhas(nivel))

    def bloco9900_insere(self):
        pass

    def print(self):
        self.bloco0000()

        self.bloco_001('0')
        # 0200 vem de arquivo
        self.bloco_insere('0990')

        # K001 vem de arquivo
        # K100 vem de arquivo
        # K200 vem de arquivo
        self.bloco_insere('K990')

        self.bloco_001('9')
        self.bloco_insere('9990')

        self.bloco_insere('9999')

        self.bloco9900_insere()
        self.bloco_990_calcula('0')
        self.bloco_990_calcula('K')

        for bloco in sorted(self.blocos.keys()):
            if bloco not in ('0200', 'K200'):
                for linha in self.blocos[bloco]:
                    print(linha)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Exporta estoque como CSV ou piped, '
                    'para inventário ou bloco K',
        epilog="(c) Tussor & Oxigenai",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "ano",
        help='Ano do mês pós inventário',
        type=int,
        metavar="{2019-2029}",
        choices=range(2019, 2030),
        )
    parser.add_argument(
        "mes",
        help='Mês pós inventário',
        type=int,
        metavar="{1-12}",
        choices=range(1, 13),
        )
    parser.add_argument(
        "arq0200",
        help='Bloco 0200')
    parser.add_argument(
        "arqk200",
        help='Bloco K200')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    sped = Sped()
    sped.ano = args.ano
    sped.mes = args.mes
    sped.import_bloco('0200', args.arq0200)
    sped.import_bloco('K200', args.arqk200)
    sped.print()
