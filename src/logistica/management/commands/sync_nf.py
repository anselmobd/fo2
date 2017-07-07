from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from fo2.models import rows_to_dict_list
import logistica.models as models


class Command(BaseCommand):
    help = 'Sync NF list from Systêxtil'

    def handle(self, *args, **options):
        try:
            cursor = connections['so'].cursor()

            # get last included
            last_nf = models.NotaFiscal.objects.order_by('-numero').\
                values_list('numero').first()
            if last_nf is None:
                last_nf = 0
            else:
                last_nf = last_nf[0]
            # self.stdout.write('last_nf = {}'.format(last_nf))

            # get since 100 before last included
            sql = '''
                SELECT
                  f.NUM_NOTA_FISCAL NF
                , f.DATA_AUTORIZACAO_NFE FATURAMENTO
                FROM FATU_050 f
                WHERE f.NUM_NOTA_FISCAL > %s
                ORDER BY
                  f.NUM_NOTA_FISCAL
            '''
            cursor.execute(sql, [last_nf-100])
            nfs_st = rows_to_dict_list(cursor)

            nfs = list(models.NotaFiscal.objects.values_list('numero'))

            for row in nfs_st:
                if (row['NF'],) not in nfs:
                    self.stdout.write('sync_nf - insert {}'.format(row['NF']))
                    nf = models.NotaFiscal(
                        numero=row['NF'], faturamento=row['FATURAMENTO'])
                    nf.save()

            # get all canceled
            sql = '''
                SELECT
                  f.NUM_NOTA_FISCAL NF
                FROM FATU_050 f
                WHERE f.SITUACAO_NFISC = 2
                ORDER BY
                  f.NUM_NOTA_FISCAL
            '''
            cursor.execute(sql)
            nfs_st = rows_to_dict_list(cursor)

            nfs = list(models.NotaFiscal.objects.filter(ativa=True).
                       values_list('numero'))

            for row in nfs_st:
                if (row['NF'],) in nfs:
                    self.stdout.write('sync_nf - cancela {}'.format(row['NF']))
                    nf = models.NotaFiscal.objects.get(numero=row['NF'])
                    nf.ativa = False
                    nf.save()

        except Exception as e:
            raise CommandError('Error syncing NF {}'.format(e))
