import sys
import datetime
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, connections

from utils.functions.models import rows_to_dict_list_lower
import lotes.models as models


class Command(BaseCommand):
    help = 'Syncronizing OPs'
    __MAX_TASKS = 100

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def iter_cursor(self, cursor):
        columns = [i[0].lower() for i in cursor.description]
        for row in cursor:
            dict_row = dict(zip(columns, row))
            yield dict_row

    def get_ops_s(self):
        cursor_s = connections['so'].cursor()
        sql = '''
            SELECT
              o.ORDEM_PRODUCAO op
            , o.PEDIDO_VENDA pedido
            , CASE WHEN o.OBSERVACAO2 LIKE '%(VAREJO)%'
              THEN 1 ELSE 0 END varejo
            , case -- o.COD_CANCELAMENTO
              when o.SITUACAO = 9 then 9 -- != 0 equivalia a "cancelada"
              else 0 -- == 0 equivalia a "não cancelada"
              end cancelada
            FROM PCPC_020 o -- OP capa
            ORDER BY
              o.ORDEM_PRODUCAO
        '''
        cursor_s.execute(sql)
        return self.iter_cursor(cursor_s)

    def get_ops_f(self):
        cursor_f = connection.cursor()
        sql = '''
            SELECT
              o.op
            , o.pedido
            , o.varejo
            , o.cancelada
            from fo2_prod_op o
            order by
              o.op
        '''
        cursor_f.execute(sql)
        return self.iter_cursor(cursor_f)

    def set_op(self, op, row):
        alter = False
        if op.op != row['op']:
            alter = True
            op.op = row['op']
        if op.pedido != row['pedido']:
            alter = True
            op.pedido = row['pedido']
        if op.varejo != (row['varejo'] == 1):
            alter = True
            op.varejo = (row['varejo'] == 1)
        if op.cancelada != (row['cancelada'] != 0):
            alter = True
            op.cancelada = (row['cancelada'] != 0)
        return alter

    def inclui(self, row):
        self.my_println('Incluindo OP {}'.format(row['op']))
        op = models.Op()
        self.set_op(op, row)
        op.save()

    def atualiza(self, row):
        self.my_println('Atualizando OP {}'.format(row['op']))

        try:
            op = models.Op.objects.get(op=row['op'])
        except models.Op.DoesNotExist:
            self.my_println('OP {} não encontrada em Fo2'.format(op))
            return
        if self.set_op(op, row):
            # self.stdout.write('save')
            op.save()

    def exclui(self, op):
        self.my_println('Excluindo OP {}'.format(op))
        try:
            ops = models.Op.objects.filter(op=op)
            for op in ops:
                op.delete()
        except models.Op.DoesNotExist:
            self.my_println('OP {} não encontrada em Fo2'.format(op))
            return

    def init_tasks(self):
        self.inclui_op = []
        self.atualiza_op = []
        self.exclui_op = []

    def exec_tasks(self):
        if len(self.inclui_op) != 0:
            for op in self.inclui_op:
                self.inclui(op)

        if len(self.atualiza_op) != 0:
            for op in self.atualiza_op:
                self.atualiza(op)

        if len(self.exclui_op) != 0:
            for op in self.exclui_op:
                self.exclui(op)

    def iguais(self, row_s, row_f):
        igual = row_s['pedido'] == row_f['pedido']
        if igual:
            igual = (row_s['varejo'] == 1) == row_f['varejo']
        if igual:
            igual = (row_s['cancelada'] != 0) == row_f['cancelada']
        return igual

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))
        try:

            # pega OPs no Systêxtil
            ics = self.get_ops_s()

            # pega OPs no Fo2
            icf = self.get_ops_f()

            op_s = -1
            op_f = -1
            self.init_tasks()
            count_task = 0
            while count_task < self.__MAX_TASKS:

                if op_s != sys.maxsize and (op_s < 0 or op_s <= op_f):
                    try:
                        row_s = next(ics)
                        getop_s = row_s['op']
                    except StopIteration:
                        getop_s = sys.maxsize

                if op_f != sys.maxsize and (op_f < 0 or op_f <= op_s):
                    try:
                        row_f = next(icf)
                        getop_f = row_f['op']
                    except StopIteration:
                        getop_f = sys.maxsize

                op_s = getop_s
                op_f = getop_f

                if op_s == sys.maxsize and op_f == sys.maxsize:
                    break

                if op_s < op_f:
                    self.my_println('Incluir OP {} no Fo2'.format(op_s))
                    self.inclui_op.append(row_s)
                    count_task += 1
                elif op_s > op_f:
                    self.my_println('OP {} não mais ativa'.format(op_f))
                    self.exclui_op.append(op_f)
                else:
                    if not self.iguais(row_s, row_f):
                        self.my_println('Atualizar OP {} no Fo2'.format(op_f))
                        self.atualiza_op.append(row_s)
                        count_task += 1

            self.exec_tasks()

        except Exception as e:
            raise CommandError('Error syncing OPs "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
