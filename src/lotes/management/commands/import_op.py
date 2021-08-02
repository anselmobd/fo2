import datetime
import sys
from pprint import pformat, pprint

from django.core.management.base import BaseCommand, CommandError

from fo2.connections import db_cursor_so

import base.models
from utils.functions.models import rows_to_dict_list_lower

import lotes.models as models
from lotes.queries.oracle import (
    oracle_existe_col, 
    oracle_existe_seq,
    oracle_existe_table, 
    oracle_existem_triggers,
)


class Command(BaseCommand):
    help = 'Syncronizing OPs'
    __MAX_TASKS = 1000

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

    def data_cursor(self, iter):
        data = []
        for row in iter:
            data.append(row)
        return data

    def get_ops_s(self, last_sync=None):
        cursor_s = db_cursor_so()
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
            , o.DEPOSITO_ENTRADA deposito
        '''
        if self.tem_col_sync:
            sql += ''' --
                , o.FO2_TUSSOR_ID sync_id
                , o.FO2_TUSSOR_SYNC sync
            '''
        sql += ''' --
            FROM PCPC_020 o -- OP capa
            '''
        if last_sync is not None:
            sql += f''' --
                WHERE o.FO2_TUSSOR_SYNC > {last_sync}
            '''
        sql += ''' --
            ORDER BY
              o.ORDEM_PRODUCAO
        '''
        cursor_s.execute(sql)
        return self.iter_cursor(cursor_s)

    def get_ops_s_del(self, tabela, last_id):
        cursor_s = db_cursor_so()
        sql = f'''
            SELECT
              d.ID
            , d.TABELA
            , d.SYNC_ID
            FROM SYSTEXTIL.FO2_TUSSOR_SYNC_DEL d
            WHERE d.TABELA = '{tabela}'
              AND d.SYNC_ID > {last_id}
            ORDER BY
              d.SYNC_ID
        '''
        cursor_s.execute(sql)
        return self.iter_cursor(cursor_s)

    def get_ops_f(self, ops=None):
        if ops is None:
            ops_f = models.Op.objects.all()
        else:
            ops_f = models.Op.objects.filter(op__in=ops)
        ops_f = ops_f.order_by('op').values()
        return iter(ops_f)

    def op_existe(self, op):
        try:
            models.Op.objects.get(op=op)
        except models.Op.DoesNotExist:
            return False
        except Exception as e:
            raise CommandError(f'Erro verificando existência de OP {op}. "{e}"')
        return True

    def get_last_sync_ids(self):
        last_sync = -1
        if models.Op.objects.filter(sync=0).count() == 0:
            try:
                last_sync = models.Op.objects.all().order_by('-sync').values(
                    'sync')[0]['sync']
            except Exception as e:
                last_sync = -1

        try:
            last_sync_del = base.models.SyncDel.objects.all().order_by(
                '-sync_id').values('sync_id')[0]['sync_id']
        except Exception as e:
            last_sync_del = -1

        return last_sync, last_sync_del

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
        if op.deposito != row['deposito']:
            alter = True
            op.deposito = row['deposito']
        if self.tem_col_sync:
            if op.sync != row['sync']:
                alter = True
                op.sync = row['sync']
            if op.sync_id != row['sync_id']:
                alter = True
                op.sync_id = row['sync_id']
        return alter

    def inclui(self, row):
        self.my_println('Incluindo OP {}'.format(row['op']))
        op = models.Op()
        self.set_op(op, row)
        op.save()

    def atualiza(self, row):
        op_num = row['op']
        self.my_println(f'Atualizando OP {op_num}')

        try:
            op = models.Op.objects.get(op=op_num)
        except models.Op.DoesNotExist:
            self.my_println('OP {} não encontrada em Fo2'.format(op))
            return
        except models.Op.MultipleObjectsReturned as e:
            raise CommandError(
                f'Erro ao atualizar OP {op_num}. "{e}"')
        if self.set_op(op, row):
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

    def exclui_sync_id(self, sync_id):
        self.my_println(f'Excluindo OP por sync_id {sync_id}')
        try:
            op = models.Op.objects.get(sync_id=sync_id)
            op.delete()
        except models.Op.DoesNotExist:
            self.my_println(f'OP com sync_id {sync_id} não encontrada em Fo2')

        try:
            table = base.models.SyncDelTable.objects.get(nome='PCPC_020')
        except base.models.SyncDelTable.DoesNotExist:
            table = base.models.SyncDelTable.objects.create(
                nome='PCPC_020',
            )

        base.models.SyncDel.objects.create(
            tabela=table,
            sync_id=sync_id,
        )

    def init_tasks(self):
        self.inclui_op = []
        self.atualiza_op = []
        self.exclui_op = []
        self.exclui_op_sync_id = []

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

        if len(self.exclui_op_sync_id) != 0:
            for sync_id in self.exclui_op_sync_id:
                self.exclui_sync_id(sync_id)

    def iguais(self, row_s, row_f):
        igual = row_s['pedido'] == row_f['pedido']
        if igual:
            igual = (row_s['varejo'] == 1) == row_f['varejo']
        if igual:
            igual = (row_s['cancelada'] != 0) == row_f['cancelada']
        if igual:
            igual = row_s['deposito'] == row_f['deposito']
        if self.tem_col_sync:
            if igual:
                igual = row_s['sync'] == row_f['sync']
            if igual:
                igual = row_s['sync_id'] == row_f['sync_id']
        return igual

    def get_tasks_sync(self, ics, icf, icsd):
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
                if self.op_existe(op_s):
                    raise CommandError(
                        f'Tentativa de incluir OP {op_s}, já existente.')
                self.my_println('Incluir OP {} no Fo2'.format(op_s))
                self.inclui_op.append(row_s)
                count_task += 1
            else:
                if not self.iguais(row_s, row_f):
                    self.my_println('Atualizar OP {} no Fo2'.format(op_f))
                    self.atualiza_op.append(row_s)
                    count_task += 1

        for row in icsd:
            self.my_println(f"OP com sync_id {row['sync_id']} não mais ativa")
            self.exclui_op_sync_id.append(row['sync_id'])

    def get_tasks(self, ics, icf):
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

    def verifica_seq(self):
        cursor_vs = db_cursor_so()
        return oracle_existe_seq(cursor_vs, 'SYSTEXTIL', 'FO2_TUSSOR')

    def verifica_del_table(self):
        cursor_vs = db_cursor_so()
        return oracle_existe_table(cursor_vs, 'SYSTEXTIL', 'FO2_TUSSOR_SYNC_DEL')

    def verifica_column(self):
        cursor_vs = db_cursor_so()
        return (
            oracle_existe_col(cursor_vs, 'PCPC_020', 'FO2_TUSSOR_SYNC')
            and
            oracle_existe_col(cursor_vs, 'PCPC_020', 'FO2_TUSSOR_ID')
        )

    def verifica_trigger(self):
        cursor_vs = db_cursor_so()
        return oracle_existem_triggers(
            cursor_vs, 'SYSTEXTIL',
            [
                ('FO2_TUSSOR_SYNC_DEL', 'FO2_TUSSOR_SYNC_DEL_TR'),
                ('PCPC_020', 'TUSSOR_TR_PCPC_020_SYNC'),
                ('PCPC_020', 'TUSSOR_TR_PCPC_020_SYNC_DEL'),
            ]
        )

    def verificacoes(self):

        # CREATE SEQUENCE SYSTEXTIL.FO2_TUSSOR INCREMENT BY 1 MINVALUE 1
        # NOCYCLE CACHE 1000 NOORDER;
        # COMMIT;

        aux_bool = self.verifica_seq()
        if self.verbosity > 1:
            self.my_println(
                'Banco tem sequência'
                if aux_bool
                else 'Banco não tem sequência'
            )

        # CREATE TABLE SYSTEXTIL.FO2_TUSSOR_SYNC_DEL (
        #   ID INTEGER NOT NULL,
        #   TABELA VARCHAR2(100) NOT NULL,
        #   SYNC_ID INTEGER NOT NULL,
        #   QUANDO TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        # )
        # TABLESPACE SYSTEXTIL_DADOS;
        # COMMIT;

        # ALTER TABLE SYSTEXTIL.FO2_TUSSOR_SYNC_DEL ADD (
        #   CONSTRAINT FO2_TUSSOR_SYNC_DEL_PK PRIMARY KEY (ID));
        # COMMIT;

        aux_bool = self.verifica_del_table()
        if self.verbosity > 1:
            self.my_println(
                'Banco tem tabela de deleção'
                if aux_bool
                else 'Banco não tem tabela de deleção'
            )

        # ALTER TABLE SYSTEXTIL.PCPC_020 ADD FO2_TUSSOR_ID INTEGER;
        # ALTER TABLE SYSTEXTIL.PCPC_020 ADD FO2_TUSSOR_SYNC INTEGER;
        # COMMIT;
        # COMMENT ON COLUMN SYSTEXTIL.PCPC_020.FO2_TUSSOR_SYNC IS
        # 'Campo específico da Tussor: flag de alteração';
        # COMMENT ON COLUMN SYSTEXTIL.PCPC_020.FO2_TUSSOR_ID IS
        # 'Campo específico da Tussor: id imutável';

        # após a criação das triggers, acerta os registros anteriores à trigger

        # UPDATE SYSTEXTIL.PCPC_020
        # SET FO2_TUSSOR_ID = NULL
        # WHERE FO2_TUSSOR_ID IS NULL;
        # COMMIT;

        self.tem_col_sync = self.verifica_column()
        if self.verbosity > 1:
            self.my_println(
                'Tabela tem colunas'
                if self.tem_col_sync
                else 'Tabela não tem colunas'
            )

        # CREATE OR REPLACE TRIGGER SYSTEXTIL.FO2_TUSSOR_SYNC_DEL_TR
        # BEFORE INSERT ON SYSTEXTIL.FO2_TUSSOR_SYNC_DEL
        # FOR EACH ROW
        # BEGIN
        #   SELECT SYSTEXTIL.FO2_TUSSOR.NEXTVAL
        #   INTO   :new.id
        #   FROM   dual;
        # END FO2_TUSSOR_SYNC_DEL_TR;

        # CREATE OR REPLACE TRIGGER SYSTEXTIL.TUSSOR_TR_PCPC_020_SYNC
        #   BEFORE INSERT OR UPDATE
        #   ON SYSTEXTIL.PCPC_020
        #   FOR EACH ROW
        # DECLARE
        #   v_sync SYSTEXTIL.PCPC_020.FO2_TUSSOR_SYNC%TYPE;
        # BEGIN
        #   SELECT SYSTEXTIL.FO2_TUSSOR.NEXTVAL
        #   INTO   v_sync
        #   FROM   DUAL;
        #   IF INSERTING or :old.FO2_TUSSOR_ID is NULL THEN
        #     :new.FO2_TUSSOR_ID := v_sync;
        #   ELSE
        #     :new.FO2_TUSSOR_ID := :old.FO2_TUSSOR_ID;
        #   END IF;
        #   :new.FO2_TUSSOR_SYNC := v_sync;
        # END TUSSOR_TR_PCPC_020_SYNC
        # ;

        # CREATE OR REPLACE TRIGGER SYSTEXTIL.TUSSOR_TR_PCPC_020_SYNC_DEL
        #   AFTER DELETE
        #   ON SYSTEXTIL.PCPC_020
        #   FOR EACH ROW
        # BEGIN
        #   INSERT INTO FO2_TUSSOR_SYNC_DEL (TABELA, SYNC_ID)
        #   VALUES ('PCPC_020', :old.FO2_TUSSOR_ID);
        # END TUSSOR_TR_PCPC_020_SYNC_DEL;

        self.tem_trigger = self.verifica_trigger()
        self.my_println(
            'Tabelas tem triggers'
            if self.tem_trigger
            else 'Tabelas não tem triggers'
        )

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))
        try:

            self.verificacoes()

            if self.tem_trigger:
                self.last_sync, self.last_sync_del = self.get_last_sync_ids()

                # pega OPs no Systêxtil
                ics = self.get_ops_s(self.last_sync)

                ops = []
                for row in ics:
                    ops.append(row['op'])

                # pega OPs no Systêxtil - NOVAMENTE, pois já foi percorrido
                ics = self.get_ops_s(self.last_sync)

                # pega deleções de OPs no Fo2
                icsd = self.get_ops_s_del('PCPC_020', self.last_sync_del)

                # pega OPs no Fo2
                icf = self.get_ops_f(ops)

                self.get_tasks_sync(ics, icf, icsd)

            else:
                # pega OPs no Systêxtil
                ics = self.get_ops_s()

                # pega OPs no Fo2
                icf = self.get_ops_f()

                self.get_tasks(ics, icf)

            self.exec_tasks()

        except Exception as e:
            raise CommandError('Error syncing OPs "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
