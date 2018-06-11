import sys
from pprint import pprint

from dbfread import DBF

from django.core.management.base import BaseCommand, CommandError
from django.db import connections


def calc_check_digit(number):
    """Calculate the EAN check digit for 13-digit numbers. The number passed
    should not have the check bit included.
    ---
    From:
      https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/ean.py
    """
    return str((10 - sum((3, 1)[i % 2] * int(n)
                for i, n in enumerate(reversed(number)))) % 10)


class Command(BaseCommand):
    help = 'Import EANs from Tussor'

    def add_arguments(self, parser):
        parser.add_argument('ref_tussor')
        parser.add_argument('ref_systextil')

    def handle(self, *args, **options):
        dis_bar_file = '/run/user/1000/gvfs/smb-share:server=192.168.1.100,' \
            'share=teg/Tussor/bd/DIS_BAR.DBF'

        ean_range = {'1': '78968962', '2': '78996188'}

        ref_tussor = options['ref_tussor'].upper()
        if len(ref_tussor) < 3:
            raise CommandError('Referência Tussor {} errada.'.format(
                ref_tussor))
        ref_systextil = options['ref_systextil'].upper()
        if len(ref_systextil) != 5:
            raise CommandError('Referência Systêxtil {} errada.'.format(
                ref_systextil))

        self.stdout.write(
            'Importando EANs do Tussor, referência: {}'.format(
                ref_tussor))
        self.stdout.write(
            'Escrevendo EANs no Systêxtil, referência = {}'.format(
                ref_systextil))

        try:

            with DBF(dis_bar_file) as bars:
                # pprint(bars)
                # pprint(len(bars))
                ref_bars = []
                for bar in bars:
                    if bar['B_PROD'] == ref_tussor and bar['B_COR'] != '':
                        # pprint(bar)
                        ean = ean_range[bar['B_RANGE']] + \
                            bar['B_CODBAR'] + calc_check_digit(
                                ean_range[bar['B_RANGE']]+bar['B_CODBAR'])
                        ref_bars.append({
                            'cor': '0000'+bar['B_COR'],
                            'tamanho': bar['B_TAM'],
                            'ean': ean,
                        })
                        # break
                    # sys.exit(0)

            # pprint(ref_bars)

            cursor = connections['so'].cursor()

            sql_set = '''
                UPDATE SYSTEXTIL.BASI_010
                SET
                  CODIGO_BARRAS=%s
                WHERE GRUPO_ESTRUTURA=%s
                  and SUBGRU_ESTRUTURA=%s
                  and ITEM_ESTRUTURA=%s
                  and CODIGO_BARRAS<>%s
            '''
            for ref_bar in ref_bars:
                cursor.execute(sql_set, [
                    ref_bar['ean'],
                    ref_systextil,
                    ref_bar['tamanho'],
                    ref_bar['cor'],
                    ref_bar['ean']
                    ])
                pprint(ref_bar)

        except Exception as e:
            raise CommandError('Error importing EANs. {}'.format(e))
