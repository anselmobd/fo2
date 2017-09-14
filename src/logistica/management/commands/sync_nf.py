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
                , f.BASE_ICMS VALOR
                , f.QTDE_EMBALAGENS VOLUMES
                , f.DATA_AUTORIZACAO_NFE FATURAMENTO
                , CAST( COALESCE( f.COD_STATUS, '0' ) AS INT ) COD_STATUS
                , COALESCE( f.MSG_STATUS, ' ' ) MSG_STATUS
                , f.SITUACAO_NFISC SITUACAO
                , f.NATOP_NF_NAT_OPER NAT
                , f.NATOP_NF_EST_OPER UF
                , n.DESCR_NAT_OPER NATUREZA
                , f.CGC_9 CNPJ9
                , f.CGC_4 CNPJ4
                , f.CGC_2 CNPJ2
                , c.NOME_CLIENTE CLIENTE
                , COALESCE(
                    CASE WHEN f.TRANSPOR_FORNE9
                            + f.TRANSPOR_FORNE4
                            + f.TRANSPOR_FORNE2 = 0
                    THEN 'O PROPRIO'
                    ELSE t.NOME_FANTASIA
                    END
                  , '-') TRANSP
                FROM FATU_050 f
                JOIN PEDI_010 c
                  ON c.CGC_9 = f.CGC_9
                 AND c.CGC_4 = f.CGC_4
                 AND c.CGC_2 = f.CGC_2
                JOIN PEDI_080 n
                  ON n.NATUR_OPERACAO = f.NATOP_NF_NAT_OPER
                 AND n.ESTADO_NATOPER = f.NATOP_NF_EST_OPER
                LEFT JOIN SUPR_010 t
                  ON t.TIPO_FORNECEDOR = 31 -- transportadora
                 AND t.FORNECEDOR9 = f.TRANSPOR_FORNE9
                 AND t.FORNECEDOR4 = f.TRANSPOR_FORNE4
                 AND t.FORNECEDOR2 = f.TRANSPOR_FORNE2
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
                dest_cnpj = '{:08d}/{:04d}-{:02d}'.format(
                    row_st['CNPJ9'],
                    row_st['CNPJ4'],
                    row_st['CNPJ2'])
                edit = True
                if (row_st['NF'],) in nfs_fo2:
                    nf_fo2 = models.NotaFiscal.objects.get(numero=row_st['NF'])
                    if nf_fo2.faturamento == faturamento \
                            and nf_fo2.valor == row_st['VALOR'] \
                            and nf_fo2.volumes == row_st['VOLUMES'] \
                            and nf_fo2.dest_cnpj == dest_cnpj \
                            and nf_fo2.dest_nome == row_st['CLIENTE'] \
                            and nf_fo2.cod_status == row_st['COD_STATUS'] \
                            and nf_fo2.msg_status == row_st['MSG_STATUS'] \
                            and nf_fo2.uf == row_st['UF'] \
                            and nf_fo2.natu_descr == row_st['NATUREZA'] \
                            and nf_fo2.transp_nome == row_st['TRANSP'] \
                            and nf_fo2.ativa == (row_st['SITUACAO'] == 1) \
                            and nf_fo2.natu_venda == (row_st['NAT'] in (1, 2)):
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

                    self.stdout.write('valor = {}'.format(row_st['VALOR']))
                    nf_fo2.valor = row_st['VALOR']

                    self.stdout.write('volumes = {}'.format(row_st['VOLUMES']))
                    nf_fo2.volumes = row_st['VOLUMES']

                    self.stdout.write('cnpj = {}'.format(dest_cnpj))
                    nf_fo2.dest_cnpj = dest_cnpj

                    self.stdout.write('clie = {}'.format(row_st['CLIENTE']))
                    nf_fo2.dest_nome = row_st['CLIENTE']

                    self.stdout.write('uf = {}'.format(row_st['UF']))
                    nf_fo2.uf = row_st['UF']

                    self.stdout.write('cod = {}'.format(row_st['COD_STATUS']))
                    nf_fo2.cod_status = row_st['COD_STATUS']

                    self.stdout.write('msg = {}'.format(row_st['MSG_STATUS']))
                    nf_fo2.msg_status = row_st['MSG_STATUS']

                    self.stdout.write('sit = {}'.format(row_st['SITUACAO']))
                    nf_fo2.ativa = (row_st['SITUACAO'] == 1)

                    self.stdout.write('natu = {}'.format(row_st['NAT']))
                    nf_fo2.natu_venda = (row_st['NAT'] in (1, 2))

                    self.stdout.write(
                        'natu_descr = {}'.format(row_st['NATUREZA']))
                    nf_fo2.natu_descr = row_st['NATUREZA']

                    self.stdout.write(
                        'transp_nome = {}'.format(row_st['TRANSP']))
                    nf_fo2.transp_nome = row_st['TRANSP']

                    nf_fo2.save()
                    self.stdout.write('saved')

        except Exception as e:
            raise CommandError('Error syncing NF "{}"'.format(e))
