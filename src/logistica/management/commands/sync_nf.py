import datetime
import hashlib
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from fo2.connections import db_cursor_so

from utils.functions.models import rows_to_dict_list

import logistica.models as models


class Command(BaseCommand):
    help = 'Sync NF list from Systêxtil'
    __MAX_TASKS = 100

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def print_diff(self, title, antigo, novo):
        if antigo != novo:
            self.my_println(
                '{} = {}'.format(title, novo))

    def print_diff_alt(self, title, antigo, novo):
        if antigo != novo:
            self.my_println(f'{title} = {antigo} -> {novo}')

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))
        try:
            cursor = db_cursor_so()

            # sync all
            sql = '''
                WITH nf_qtd AS
                ( SELECT
                    f.codigo_empresa
                  , f.num_nota_fiscal
                  , f.serie_nota_fisc
                  , sum(fi.QTDE_ITEM_FATUR) QTD
                  FROM FATU_050 f
                  JOIN fatu_060 fi
                    ON fi.ch_it_nf_cd_empr = f.codigo_empresa
                   AND fi.ch_it_nf_num_nfis = f.num_nota_fiscal
                   AND fi.ch_it_nf_ser_nfis = f.serie_nota_fisc
                  GROUP BY 
                    f.codigo_empresa
                  , f.num_nota_fiscal
                  , f.serie_nota_fisc
                )
                , ped_dep AS
                (
                SELECT
                  ped.PEDIDO_VENDA
                , min(iped.CODIGO_DEPOSITO) CODIGO_DEPOSITO
                FROM PEDI_100 ped -- pedido de venda
                JOIN PEDI_110 iped -- item de pedido de venda
                  ON iped.PEDIDO_VENDA = ped.PEDIDO_VENDA
                GROUP BY 
                  ped.PEDIDO_VENDA
                )
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
                , pd.CODIGO_DEPOSITO DEPOSITO
                , CASE WHEN pd.CODIGO_DEPOSITO = 101 THEN 'a'
                  WHEN pd.CODIGO_DEPOSITO = 102 THEN 'v'
                  ELSE 'o' END TIPO
                , fe.DOCUMENTO NF_DEVOLUCAO
                , fi.QTD
                FROM FATU_050 f
                JOIN nf_qtd fi
                  ON fi.codigo_empresa = f.codigo_empresa
                 AND fi.num_nota_fiscal = f.num_nota_fiscal
                 AND fi.serie_nota_fisc = f.serie_nota_fisc
                LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
                  ON fe.NOTA_DEV = f.NUM_NOTA_FISCAL
                 AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada
                LEFT JOIN PEDI_100 p
                  ON p.PEDIDO_VENDA = f.PEDIDO_VENDA
                LEFT JOIN ped_dep pd
                  ON pd.PEDIDO_VENDA = p.PEDIDO_VENDA
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
                -- WHERE f.NUMERO_CAIXA_ECF = 0
                ORDER BY
                  f.NUM_NOTA_FISCAL DESC
            '''
            cursor.execute(sql)
            nfs_st = rows_to_dict_list(cursor)

            nfs_fo2_list = list(models.NotaFiscal.objects.values_list(
                'numero', 'trail'))
            nfs_fo2 = {nf[0]: nf[1] for nf in nfs_fo2_list}

            count_task = 0
            for row_st in nfs_st:
                faturamento = row_st['FATURAMENTO']
                dest_cnpj = '{:08d}/{:04d}-{:02d}'.format(
                    row_st['CNPJ9'],
                    row_st['CNPJ4'],
                    row_st['CNPJ2'])
                natu_venda = (row_st['NAT'] in (1, 2)) \
                    or (row_st['DIV_NAT'] == '8'
                        and (row_st['COD_NAT'] == '6.11'
                             or row_st['COD_NAT'] == '5.11'
                             )
                        )

                hash_cache = ';'.join(map(format, (
                    row_st['NF'],
                    faturamento,
                    row_st['VALOR'],
                    row_st['VOLUMES'],
                    row_st['QTD'],
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
                    row_st['NF_DEVOLUCAO'],
                    row_st['TIPO'],
                )))
                hash_object = hashlib.md5(hash_cache.encode())
                trail = hash_object.hexdigest()

                edit = True
                if row_st['NF'] in nfs_fo2.keys():
                    if trail == nfs_fo2[row_st['NF']]:
                        edit = False
                    else:
                        nf_fo2 = models.NotaFiscal.objects.get(
                            numero=row_st['NF'])
                        self.my_println(
                            'sync_nf - update {}'.format(row_st['NF']))

                else:
                    self.my_println(
                        'sync_nf - insert {}'.format(row_st['NF']))
                    nf_fo2 = models.NotaFiscal(numero=row_st['NF'])

                if edit:
                    self.print_diff_alt('data', nf_fo2.faturamento, faturamento)
                    nf_fo2.faturamento = faturamento

                    self.print_diff('valor', nf_fo2.valor, row_st['VALOR'])
                    nf_fo2.valor = row_st['VALOR']

                    self.print_diff(
                        'volumes', nf_fo2.volumes, row_st['VOLUMES'])
                    nf_fo2.volumes = row_st['VOLUMES']

                    self.print_diff(
                        'qtd', nf_fo2.volumes, row_st['QTD'])
                    nf_fo2.quantidade = row_st['QTD']

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

                    self.print_diff(
                        'nf_devolucao',
                        nf_fo2.nf_devolucao, row_st['NF_DEVOLUCAO'])
                    nf_fo2.nf_devolucao = row_st['NF_DEVOLUCAO']

                    self.print_diff(
                        'tipo', nf_fo2.tipo, row_st['TIPO'])
                    nf_fo2.tipo = row_st['TIPO']

                    self.print_diff('trail', nf_fo2.trail, trail)
                    nf_fo2.trail = trail

                    nf_fo2.save()
                    count_task += 1

                    if count_task >= self.__MAX_TASKS:
                        self.my_println('{} tarefas'.format(self.__MAX_TASKS))
                        break

        except Exception as e:
            raise CommandError('Error syncing NF "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
