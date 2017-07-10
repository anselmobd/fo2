from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.utils import timezone

from fo2.models import rows_to_dict_list
import logistica.models as models


class Command(BaseCommand):
    help = 'Sync NF list from Systêxtil'

    def handle(self, *args, **options):
        try:
            cursor = connections['so'].cursor()

            # sync all
            sql = '''
                SELECT
                  f.NUM_NOTA_FISCAL NF
                , f.DATA_AUTORIZACAO_NFE FATURAMENTO
                , CAST( COALESCE( f.COD_STATUS, '0' ) AS INT ) COD_STATUS
                , COALESCE( f.MSG_STATUS, ' ' ) MSG_STATUS
                , f.SITUACAO_NFISC SITUACAO
                FROM FATU_050 f
                --WHERE rownum = 1
                ORDER BY
                  f.NUM_NOTA_FISCAL DESC
            '''
            cursor.execute(sql)
            nfs_st = rows_to_dict_list(cursor)
            # self.stdout.write('len(nfs_st) = {}'.format(len(nfs_st)))

            nfs_fo2 = list(models.NotaFiscal.objects.values_list('numero'))
            # self.stdout.write('len(nfs_fo2) = {}'.format(len(nfs_fo2)))

            for row_st in nfs_st:
                if row_st['FATURAMENTO'] is None:
                    faturamento = None
                else:
                    faturamento = timezone.make_aware(
                        row_st['FATURAMENTO'], timezone.get_current_timezone())
                edit = True
                if (row_st['NF'],) in nfs_fo2:
                    nf_fo2 = models.NotaFiscal.objects.get(numero=row_st['NF'])
                    if nf_fo2.faturamento == faturamento \
                            and nf_fo2.cod_status == row_st['COD_STATUS'] \
                            and nf_fo2.msg_status == row_st['MSG_STATUS'] \
                            and nf_fo2.ativa == (row_st['SITUACAO'] == 1):
                        edit = False
                    else:
                        self.stdout.write(
                            'sync_nf - update {}'.format(row_st['NF']))
                else:
                    self.stdout.write(
                        'sync_nf - insert {}'.format(row_st['NF']))
                    nf_fo2 = models.NotaFiscal(numero=row_st['NF'])
                if edit:
                    # pprint(row_st)
                    self.stdout.write(
                        'NF = {}'.format(row_st['NF']))
                    self.stdout.write(
                        'date = {}'.format(faturamento))
                    nf_fo2.faturamento = faturamento

                    self.stdout.write('cod = {}'.format(row_st['COD_STATUS']))
                    nf_fo2.cod_status = row_st['COD_STATUS']

                    self.stdout.write('msg = {}'.format(row_st['MSG_STATUS']))
                    nf_fo2.msg_status = row_st['MSG_STATUS']

                    self.stdout.write('sit = {}'.format(row_st['SITUACAO']))
                    nf_fo2.ativa = (row_st['SITUACAO'] == 1)

                    nf_fo2.save()
                    self.stdout.write('saved')

        except Exception as e:
            raise CommandError('Error syncing NF "{}"'.format(e))
