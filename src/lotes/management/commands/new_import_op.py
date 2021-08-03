import datetime
from pprint import pformat

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max, Value
from django.db.models.functions import Coalesce

from fo2.connections import db_cursor_so

import base.models

import lotes.models


class Command(BaseCommand):
    '''Esta versão do comando import_op assume que o banco já está
    preparado com controles de SYNC do FO2
    '''
    help = 'Syncronizing OPs (Fo2)'
    __MAX_TASKS = 1

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def my_pprintln(self, object):
        self.my_pprint(object, ending='\n')

    def my_pprint(self, object, ending=''):
        self.stdout.write(pformat(object), ending=ending)
        self.stdout.flush()

    def iter_cursor(self, cursor):
        columns = [i[0].lower() for i in cursor.description]
        for row in cursor:
            dict_row = dict(zip(columns, row))
            yield dict_row

    def get_last_sync_ids(self):
        op = lotes.models.Op.objects.aggregate(
            last_sync=Coalesce(Max('sync'), Value(-1)),
            last_op=Coalesce(Max('op'), Value(-1)),
        )
        delete = base.models.SyncDel.objects.aggregate(
            last_sync=Coalesce(Max('id'), Value(-1))
        )
        self.last_sync = op['last_sync']
        self.last_op = op['last_op']
        self.last_sync_del = delete['last_sync']

    def get_ops_s(self):
        sql = f'''
            SELECT
              o.ORDEM_PRODUCAO op
            , o.PEDIDO_VENDA pedido
            , CASE WHEN o.OBSERVACAO2 LIKE '%(VAREJO)%'
              THEN 1 ELSE 0 END varejo
            , case -- o.COD_CANCELAMENTO
              when o.SITUACAO = 9 then 9 -- != 0 equivalia a "cancelada"
              else 0 -- == 0 equivalia a "não cancelada"
              end cancelada
            , o.DEPOSITO_ENTRADA deposito
            , o.FO2_TUSSOR_ID sync_id
            , o.FO2_TUSSOR_SYNC sync
            FROM PCPC_020 o -- OP capa
            WHERE o.FO2_TUSSOR_SYNC > {self.last_sync}
            ORDER BY
              o.FO2_TUSSOR_SYNC
        '''
        self.cursor_s.execute(sql)
        return self.iter_cursor(self.cursor_s)

    def get_ops_s_del(self, tabela):
        sql = f'''
            SELECT
              d.ID
            , d.TABELA
            , d.SYNC_ID
            FROM SYSTEXTIL.FO2_TUSSOR_SYNC_DEL d
            WHERE d.TABELA = '{tabela}'
              AND d.ID > {self.last_sync_del}
            ORDER BY
              d.ID
        '''
        self.cursor_s.execute(sql)
        return self.iter_cursor(self.cursor_s)

    def set_op(self, op, row):
        # op_antes = self.op_dict(op)
        op.op = row['op']
        op.pedido = row['pedido']
        op.varejo = (row['varejo'] == 1)
        op.cancelada = (row['cancelada'] != 0)
        op.deposito = row['deposito']
        op.sync = row['sync']
        op.sync_id = row['sync_id']
        # return not self.iguais_dicts(op_antes, self.op_dict(op))

    def get_op(self, num_op):
        try:
            op = lotes.models.Op.objects.get(op=num_op)
        except lotes.models.Op.DoesNotExist as e:
            self.my_println(
                f"OP {num_op} não encontrada em Fo2. '{e}'"
            )
            op = lotes.models.Op()
        except lotes.models.Op.MultipleObjectsReturned as e:
            self.my_println(
                f"Erro ao atualizar OP {num_op}. '{e}'"
            )
            ops = lotes.models.Op.objects.filter(op=num_op).order_by('-sync')
            for op in ops[1:]:
                op.delete()
            op = ops[0]
        return op

    def get_op_by_sync_id(self, sync_id):
        try:
            op = lotes.models.Op.objects.get(sync_id=sync_id)
        except lotes.models.Op.DoesNotExist as e:
            self.my_println(
                f"OP com sync_id {sync_id} não encontrada em Fo2. '{e}'"
            )
            op = None
        return op

    def atualiza(self, row):
        op = self.get_op(row['op'])
        self.set_op(op, row)
        op.save()

    def inclui(self, row):
        op = lotes.models.Op()
        self.set_op(op, row)
        op.save()

    def apaga(self, row):
        num_op = None
        op = self.get_op_by_sync_id(row['sync_id'])
        if op:
            num_op = op.op
            op.delete()

        try:
            table = base.models.SyncDelTable.objects.get(nome='PCPC_020')
        except base.models.SyncDelTable.DoesNotExist:
            table = base.models.SyncDelTable.objects.create(
                nome='PCPC_020',
            )

        base.models.SyncDel.objects.create(
            id=row['id'],
            tabela=table,
            sync_id=row['sync_id'],
        )

        return num_op

    def sincroniza(self):
        count_task = 1
        try:

            self.cursor_s = db_cursor_so()

            self.get_last_sync_ids()
            
            # pega OPs no Systêxtil
            ics = self.get_ops_s()

            for row in ics:
                if count_task > self.__MAX_TASKS:
                    return
                count_task = 1
                
                if row['op'] > self.last_op:
                    self.my_println(f"i {row['op']}")
                    self.inclui(row)
                else:
                    self.my_println(f"u {row['op']}")
                    self.atualiza(row)

            # pega deleções de OPs no Fo2
            icsd = self.get_ops_s_del('PCPC_020')

            for row in icsd:
                if count_task > self.__MAX_TASKS:
                    return
                count_task = 1
                
                self.my_println(f"d {row['sync_id']}")
                num_op = self.apaga(row)
                if num_op:
                    self.my_println(f"= {num_op}")

        except Exception as e:
            raise CommandError('Error syncing OPs (Fo2) "{}"'.format(e))

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        self.sincroniza()

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
