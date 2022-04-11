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
        self.ordem = '0BCDEGHK19'

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

    def bloco_ordem(self, nome):
        return '{:02}{}'.format(
            self.ordem.find(nome[0]),
            nome
        )

    def import_linha(self, linha, bloco_id, pos_nivel):
        bloco = linha[1:5]
        if bloco not in self.blocos:
            self.blocos[bloco] = []
        if (
            args.com_corte
            or (
                not (
                    (bloco == bloco_id)
                    and (linha[pos_nivel] == '2')
                )
            )
        ):
            self.blocos[bloco].append(linha)

    def import_bloco(self, arq, bloco_id, pos_nivel):
        with open(arq) as data:
            for linha in data.read().splitlines():
                self.import_linha(linha, bloco_id, pos_nivel)

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

    def set_bloco_valor(self, nome, valor):
        self.blocos[nome][0] += \
            '{}|'.format(valor)

    def bloco_insere(self, nome, valor=None):
        self.blocos[nome] = ['|{}|'.format(nome)]
        if valor is not None:
            self.set_bloco_valor(nome, valor)

    def bloco_calcula(self, nome, nivel):
        self.set_bloco_valor(nome, self.conta_linhas(nivel))

    def bloco9900_insere_todos(self):
        blocos = ['9900']
        for bloco in self.blocos.keys():
            blocos.append(bloco)
        for bloco in sorted(blocos, key=self.bloco_ordem):
            self.bloco_insere('9900|{}'.format(bloco))

    def bloco9900_calcula_todos(self):
        blocos9900 = [bloco[5:9]
                      for bloco in self.blocos.keys()
                      if '|' in bloco]
        for bloco in blocos9900:
            self.set_bloco_valor(
                '9900|{}'.format(bloco),
                self.conta_linhas(bloco),
            )

    def print(self):
        self.bloco0000()

        self.bloco_insere('0001', '1')
        # 0200 vem de arquivo
        self.bloco_insere('0990')

        # K001 vem de arquivo
        # K100 vem de arquivo
        # K200 vem de arquivo
        self.bloco_insere('K990')

        self.bloco_insere('9001', '1')
        self.bloco_insere('9990')

        self.bloco_insere('9999')

        self.bloco9900_insere_todos()

        self.bloco_calcula('0990', '0')
        self.bloco_calcula('K990', 'K')
        self.bloco_calcula('9990', '9')
        self.bloco_calcula('9999', '')

        self.bloco9900_calcula_todos()

        for bloco in sorted(self.blocos.keys(), key=self.bloco_ordem):
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
    parser.add_argument(
        '--com_corte', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    sped = Sped()
    sped.ano = args.ano
    sped.mes = args.mes
    sped.import_bloco(args.arq0200, '0200', 6)
    sped.import_bloco(args.arqk200, 'K200', 15)
    sped.print()
