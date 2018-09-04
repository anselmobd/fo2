from pprint import pprint
import hashlib
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.utils import timezone

from fo2.models import rows_to_dict_list
import logistica.models as models


class Command(BaseCommand):
    help = 'Sync NF list from Systêxtil'

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def print_diff(self, title, antigo, novo):
        if antigo != novo:
            self.my_println(
                '{} = {}'.format(title, novo))

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))
        try:
            cursor = connections['so'].cursor()

            # sync all
            sql = '''
                SELECT
                  f.NUM_NOTA_FISCAL NF
                , f.BASE_ICMS VALOR
                , f.QTDE_EMBALAGENS VOLUMES
                , f.DATA_AUTORIZACAO_NFE FATURAMENTO
                , CAST( COALESCE( '0' || f.COD_STATUS, '0' ) AS INT )
                  COD_STATUS
                , COALESCE( f.MSG_STATUS, ' ' ) MSG_STATUS
                , f.SITUACAO_NFISC SITUACAO
                , f.NATOP_NF_NAT_OPER NAT
                , f.NATOP_NF_EST_OPER UF
                , n.DESCR_NAT_OPER NATUREZA
                , n.COD_NATUREZA COD_NAT
                , n.DIVISAO_NATUR DIV_NAT
                , f.CGC_9 CNPJ9
                , f.CGC_4 CNPJ4
                , f.CGC_2 CNPJ2
                , c.NOME_CLIENTE CLIENTE
                , COALESCE(
                    CASE WHEN f.TRANSPOR_FORNE9
                            + f.TRANSPOR_FORNE4
                            + f.TRANSPOR_FORNE2 = 0
                    THEN 'O PROPRIO'
                    ELSE COALESCE( t.NOME_FANTASIA
                                 , '(' || f.TRANSPOR_FORNE9 || '/' ||
                                   f.TRANSPOR_FORNE4 || '-' ||
                                   f.TRANSPOR_FORNE2 || ')' )
                    END
                  , '-') TRANSP
                , f.PEDIDO_VENDA PEDIDO
                , p.COD_PED_CLIENTE PED_CLIENTE
                FROM FATU_050 f
                LEFT JOIN PEDI_100 p
                  ON p.PEDIDO_VENDA = f.PEDIDO_VENDA
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
            # self.my_println('len(nfs_st) = {}'.format(len(nfs_st)))

            nfs_fo2 = list(models.NotaFiscal.objects.values_list('numero'))
            # self.my_println('len(nfs_fo2) = {}'.format(len(nfs_fo2)))

            for row_st in nfs_st:
                edit = True
                if row_st['FATURAMENTO'] is None:
                    faturamento = None
                else:
                    faturamento = timezone.make_aware(
                        row_st['FATURAMENTO'],
                        timezone.get_current_timezone())
                dest_cnpj = '{:08d}/{:04d}-{:02d}'.format(
                    row_st['CNPJ9'],
                    row_st['CNPJ4'],
                    row_st['CNPJ2'])
                natu_venda = (row_st['NAT'] in (1, 2)) \
                    or (row_st['DIV_NAT'] == '8'
                        and (row_st['COD_NAT'] == '6.11'
                             or row_st['COD_NAT'] == '5.11'))

                hash_cache = ';'.join(map(format, (
                    row_st['NF'],
                    faturamento,
                    row_st['VALOR'],
                    row_st['VOLUMES'],
                    dest_cnpj,
                    row_st['CLIENTE'],
                    row_st['COD_STATUS'],
                    row_st['MSG_STATUS'],
                    row_st['UF'],
                    row_st['NATUREZA'],
                    row_st['TRANSP'],
                    row_st['SITUACAO'] == 1,
                    natu_venda,
                    row_st['PEDIDO'],
                    row_st['PED_CLIENTE'],
                )))
                hash_object = hashlib.md5(hash_cache.encode())
                trail = hash_object.hexdigest()

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
                            and nf_fo2.natu_venda == natu_venda \
                            and nf_fo2.pedido == row_st['PEDIDO'] \
                            and nf_fo2.ped_cliente == row_st['PED_CLIENTE'] \
                            and nf_fo2.trail == trail:
                        edit = False

                    else:
                        self.my_println(
                            'sync_nf - update {}'.format(row_st['NF']))

                else:
                    self.my_println(
                        'sync_nf - insert {}'.format(row_st['NF']))
                    nf_fo2 = models.NotaFiscal(numero=row_st['NF'])

                if edit:
                    self.print_diff('data', nf_fo2.faturamento, faturamento)
                    nf_fo2.faturamento = faturamento

                    self.print_diff('valor', nf_fo2.valor, row_st['VALOR'])
                    nf_fo2.valor = row_st['VALOR']

                    self.print_diff(
                        'volumes', nf_fo2.volumes, row_st['VOLUMES'])
                    nf_fo2.volumes = row_st['VOLUMES']

                    self.print_diff('cnpj', nf_fo2.dest_cnpj, dest_cnpj)
                    nf_fo2.dest_cnpj = dest_cnpj

                    self.print_diff(
                        'clie', nf_fo2.dest_nome, row_st['CLIENTE'])
                    nf_fo2.dest_nome = row_st['CLIENTE']

                    self.print_diff('uf', nf_fo2.uf, row_st['UF'])
                    nf_fo2.uf = row_st['UF']

                    self.print_diff(
                        'cod', nf_fo2.cod_status, row_st['COD_STATUS'])
                    nf_fo2.cod_status = row_st['COD_STATUS']

                    self.print_diff(
                        'msg', nf_fo2.msg_status, row_st['MSG_STATUS'])
                    nf_fo2.msg_status = row_st['MSG_STATUS']

                    self.print_diff(
                        'sit', nf_fo2.ativa, (row_st['SITUACAO'] == 1))
                    nf_fo2.ativa = (row_st['SITUACAO'] == 1)

                    self.print_diff(
                        'natu_venda', nf_fo2.natu_venda, natu_venda)
                    nf_fo2.natu_venda = natu_venda

                    self.print_diff(
                        'natu_descr', nf_fo2.natu_descr, row_st['NATUREZA'])
                    nf_fo2.natu_descr = row_st['NATUREZA']

                    self.print_diff(
                        'transp_nome', nf_fo2.transp_nome, row_st['TRANSP'])
                    nf_fo2.transp_nome = row_st['TRANSP']

                    self.print_diff(
                        'pedido', nf_fo2.pedido, row_st['PEDIDO'])
                    nf_fo2.pedido = row_st['PEDIDO']

                    self.print_diff(
                        'ped_cliente',
                        nf_fo2.ped_cliente, row_st['PED_CLIENTE'])
                    nf_fo2.ped_cliente = row_st['PED_CLIENTE']

                    self.print_diff('trail', nf_fo2.trail, trail)
                    nf_fo2.trail = trail

                    nf_fo2.save()
                    self.my_println('saved')

        except Exception as e:
            raise CommandError('Error syncing NF "{}"'.format(e))

        self.my_println('{}'.format(datetime.datetime.now()))
