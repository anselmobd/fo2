import datetime
import sys
from pprint import pformat, pprint

from django.core.management.base import BaseCommand, CommandError

from fo2.connections import db_cursor, db_cursor_so

import lotes.models as models
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.queries.oracle import (
    oracle_existe_col, 
    oracle_existe_seq,
    oracle_existe_table, 
    oracle_existem_triggers,
)


class Command(BaseCommand):
    help = 'Syncronizing Lotes'
    __MAX_TASKS = 100

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--op', type=int,
            help='Indica uma OP específica a ser tratada')
        parser.add_argument(
            '-i', '--opini', type=int,
            help='Indica a OP inicial do processamento')

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

    def get_ops_trail_s(self):
        cursor_s = db_cursor_so()
        sql = '''
            SELECT
              lo.ORDEM_PRODUCAO op
            , max(lo.FO2_TUSSOR_SYNC) trail
            FROM PCPC_040 lo -- lote estágio
            JOIN PCPC_020 op -- OP capa
              ON op.ordem_producao = lo.ORDEM_PRODUCAO
            WHERE op.SITUACAO <> 9 -- op.COD_CANCELAMENTO = 0
              AND lo.QTDE_PECAS_PROG IS NOT NULL
              AND lo.QTDE_PECAS_PROG  <> 0
        '''
        if self.oponly is not None:
            sql += '''--
                  AND op.ordem_producao = {}
            '''.format(self.oponly)
        elif self.opini is not None:
            sql += '''--
                  AND op.ordem_producao >= {}
            '''.format(self.opini)
        sql += '''--
            GROUP BY
              lo.ORDEM_PRODUCAO
            ORDER BY
              lo.ORDEM_PRODUCAO
        '''
        cursor_s.execute(sql)
        return self.iter_cursor(cursor_s)

    def get_ops_trail_f(self):
        cursor_f = db_cursor('default')
        sql = '''
            SELECT
              le.op
            , max(le.sync) trail
            FROM fo2_cd_lote le
        '''
        if self.oponly is not None:
            sql += '''--
                WHERE le.op = {}
            '''.format(self.oponly)
        elif self.opini is not None:
            sql += '''--
                WHERE le.op >= {}
            '''.format(self.opini)
        sql += '''--
            GROUP BY
              le.op
            ORDER BY
              le.op
        '''
        cursor_f.execute(sql)
        return self.iter_cursor(cursor_f)

    def get_lotes_op(self, op):
        cursor = db_cursor_so()
        sql = f'''
            SELECT
              lote.OP
            , lote.PERIODO
            , lote.OC
            , lote.REF
            , lote.TAM
            , lote.ORD_TAM
            , lote.COR
            , lote.QTD_PRODUZIR
            , lote.TRAIL
            , CASE WHEN l.ORDEM_CONFECCAO IS NULL THEN 999
              ELSE l.CODIGO_ESTAGIO END ESTAGIO
            , CASE WHEN l.ORDEM_CONFECCAO IS NULL THEN lf.QTDE_PECAS_PROD
              ELSE l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO END QTD
            , CASE WHEN l.ORDEM_CONFECCAO IS NULL THEN 0
              ELSE l.QTDE_CONSERTO END CONSERTO
            , lote.sync_id
            , lote.sync
            FROM
            (
              SELECT
                le.ORDEM_PRODUCAO OP
              , le.PERIODO_PRODUCAO PERIODO
              , le.ORDEM_CONFECCAO OC
              , le.PROCONF_GRUPO REF
              , le.PROCONF_SUBGRUPO TAM
              , t.ORDEM_TAMANHO ORD_TAM
              , le.PROCONF_ITEM COR
              , le.QTDE_PECAS_PROG QTD_PRODUZIR
              , max(le.CODIGO_ESTAGIO) ULTIMO_ESTAGIO
              , max(le.SEQUENCIA_ESTAGIO) ULTIMA_SEQ_ESTAGIO
              , 0 trail
              , max(le.FO2_TUSSOR_ID) sync_id
              , max(le.FO2_TUSSOR_SYNC) sync
              FROM PCPC_040 le -- lote estágio
              LEFT JOIN BASI_220 t
                ON t.TAMANHO_REF = le.PROCONF_SUBGRUPO
              WHERE le.ORDEM_PRODUCAO = '{op}'
            --    AND le.ORDEM_CONFECCAO = 22
                AND le.QTDE_PECAS_PROG IS NOT NULL
                AND le.QTDE_PECAS_PROG <> 0
              GROUP BY
                le.ORDEM_PRODUCAO
              , le.PERIODO_PRODUCAO
              , le.ORDEM_CONFECCAO
              , le.PROCONF_GRUPO
              , le.PROCONF_SUBGRUPO
              , t.ORDEM_TAMANHO
              , le.PROCONF_ITEM
              , le.QTDE_PECAS_PROG
              ORDER BY
                le.ORDEM_PRODUCAO
              , le.ORDEM_CONFECCAO
            ) lote
            LEFT JOIN PCPC_040 l -- lote estágio
              ON l.ORDEM_PRODUCAO = lote.OP
             AND l.ORDEM_CONFECCAO = lote.OC
             AND (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) <> 0
            LEFT JOIN PCPC_040 lf -- lote estágio
              ON l.ORDEM_CONFECCAO IS NULL
             AND lf.ORDEM_PRODUCAO = lote.OP
             AND lf.ORDEM_CONFECCAO = lote.OC
             AND (  (   lote.ULTIMA_SEQ_ESTAGIO = 0
                    AND lf.CODIGO_ESTAGIO = lote.ULTIMO_ESTAGIO)
                 OR (   lote.ULTIMA_SEQ_ESTAGIO <> 0
                    AND lf.SEQUENCIA_ESTAGIO = lote.ULTIMA_SEQ_ESTAGIO)
                 )
        '''
        debug_cursor_execute(cursor, sql)
        return dictlist_lower(cursor)

    def set_lote(self, lote, row):
        alter = False
        if lote.lote != row['lote']:
            alter = True
            lote.lote = row['lote']
            # self.stdout.write('lote {}'.format(lote.lote))
        if lote.op != row['op']:
            alter = True
            lote.op = row['op']
            # self.stdout.write('op {}'.format(lote.op))
        if lote.referencia != row['ref']:
            alter = True
            lote.referencia = row['ref']
            # self.stdout.write('ref {}'.format(lote.referencia))
        if lote.tamanho != row['tam']:
            alter = True
            lote.tamanho = row['tam']
            # self.stdout.write('tam {}'.format(lote.tamanho))
        if lote.ordem_tamanho != row['ord_tam']:
            alter = True
            lote.ordem_tamanho = row['ord_tam']
            # self.stdout.write('ord_tam {}'.format(lote.ordem_tamanho))
        if lote.cor != row['cor']:
            alter = True
            lote.cor = row['cor']
            # self.stdout.write('cor {}'.format(lote.cor))
        if lote.estagio != row['estagio']:
            alter = True
            lote.estagio = row['estagio']
            # self.stdout.write('estagio {}'.format(lote.estagio))
        if lote.qtd != row['qtd']:
            alter = True
            lote.qtd = row['qtd']
            # self.stdout.write('qtd {}'.format(lote.qtd))
        if lote.conserto != row['conserto']:
            alter = True
            lote.conserto = row['conserto']
            # self.stdout.write('conserto {}'.format(lote.conserto))
        if lote.qtd_produzir != row['qtd_produzir']:
            alter = True
            lote.qtd_produzir = row['qtd_produzir']
            # self.stdout.write('qtd_produzir {}'.format(lote.qtd_produzir))
        if lote.sync != row['sync']:
            alter = True
            lote.sync = row['sync']
        if lote.sync_id != row['sync_id']:
            alter = True
            lote.sync_id = row['sync_id']
        return alter

    def inclui(self, op):
        self.my_println('Incluindo OP {}'.format(op))
        lotes = self.get_lotes_op(op)
        ocs = []
        for row in lotes:
            if row['oc'] not in ocs:
                ocs.append(row['oc'])
        self.my_print('Sistêxtil: {} lotes'.format(len(ocs)))
        for oc in ocs:
            oc_estagios = [row for row in lotes if row['oc'] == oc]
            oc_est63 = [row for row in oc_estagios if row['estagio'] == 63]
            if len(oc_est63) == 0:
                row = oc_estagios[-1]
            else:
                row = oc_est63[0]
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            lote = models.Lote()
            self.set_lote(lote, row)
            lote.save()
            self.my_print(' {}{}'.format('I', row['lote'][4:].lstrip('0')))
        self.my_println()

    def atualiza(self, op):
        self.my_println('Atualizando OP {}'.format(op))

        # atualizando Systêxtil -> Fo2
        lotes = self.get_lotes_op(op)
        ocs = []
        for row in lotes:
            if row['oc'] not in ocs:
                ocs.append(row['oc'])
        self.my_print('Sistêxtil: {} lotes'.format(len(ocs)))
        sys_lotes = []
        for oc in ocs:
            oc_estagios = [row for row in lotes if row['oc'] == oc]
            oc_est63 = [row for row in oc_estagios if row['estagio'] == 63]
            if len(oc_est63) == 0:
                row = oc_estagios[-1]
            else:
                row = oc_est63[0]

            acao = ''
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            sys_lotes.append(row['lote'])
            # self.stdout.write('OC {}'.format(row['oc']))
            try:
                # self.stdout.write('try')
                lote = models.Lote.objects.get(lote=row['lote'])
                acao = 'A'
            except models.Lote.DoesNotExist:
                # self.stdout.write('except')
                lote = None
            if not lote:
                # self.stdout.write('not lote')
                acao = 'I'
                lote = models.Lote()
            if self.set_lote(lote, row):
                # self.stdout.write('save')
                lote.save()
                self.my_print(
                    ' {}{}'.format(acao, row['lote'][4:].lstrip('0')))

        # atualizando Fo2 -> Systêxtil
        lotes = models.Lote.objects.filter(op=op)
        self.my_println()
        self.my_print('Fo2: {} lotes'.format(len(lotes)))
        for row in lotes:
            if row.lote not in sys_lotes:
                row.delete()
                self.my_print(' E{}'.format(row.lote[4:].lstrip('0')))
        self.my_println()

    def exclui(self, op):
        self.my_println('Excluindo OP {}'.format(op))
        lotes = models.Lote.objects.filter(op=op)
        lotes_localizados = lotes.exclude(
                local__isnull=True
            ).exclude(
                local__exact='')
        self.my_println('Fo2: {} lotes'.format(len(lotes)))
        self.my_println('Fo2: {} lotes localizados'.format(
            len(lotes_localizados)))
        if len(lotes_localizados) == 0:
            for row in lotes:
                row.delete()
        else:
            self.my_println('OP {} não excluida'.format(op))

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

    def verifica_seq(self):
        cursor_vs = db_cursor_so()
        return oracle_existe_seq(cursor_vs, 'SYSTEXTIL', 'FO2_TUSSOR')

    def verifica_del_table(self):
        cursor_vs = db_cursor_so()
        return oracle_existe_table(cursor_vs, 'SYSTEXTIL', 'FO2_TUSSOR_SYNC_DEL')

    def verifica_column(self):
        cursor_vs = db_cursor_so()
        return (
            oracle_existe_col(cursor_vs, 'PCPC_040', 'FO2_TUSSOR_SYNC')
            and
            oracle_existe_col(cursor_vs, 'PCPC_040', 'FO2_TUSSOR_ID')
        )

    def verifica_trigger(self):
        cursor_vs = db_cursor_so()
        return oracle_existem_triggers(
            cursor_vs, 'SYSTEXTIL',
            [
                ('FO2_TUSSOR_SYNC_DEL', 'FO2_TUSSOR_SYNC_DEL_TR'),
                ('PCPC_040', 'TUSSOR_TR_PCPC_040_SYNC'),
                ('PCPC_040', 'TUSSOR_TR_PCPC_040_SYNC_DEL'),
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

        # ALTER TABLE SYSTEXTIL.PCPC_040 ADD FO2_TUSSOR_ID INTEGER;
        # ALTER TABLE SYSTEXTIL.PCPC_040 ADD FO2_TUSSOR_SYNC INTEGER;
        # COMMIT;

        # após a criação das triggers, acerta os registros anteriores à trigger

        # UPDATE SYSTEXTIL.PCPC_040
        # SET FO2_TUSSOR_ID = FO2_TUSSOR_SYNC
        # WHERE FO2_TUSSOR_ID IS NULL
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

        # CREATE OR REPLACE TRIGGER SYSTEXTIL.TUSSOR_TR_PCPC_040_SYNC
        #   BEFORE INSERT OR UPDATE 
        #   ON SYSTEXTIL.PCPC_040
        #   FOR EACH ROW
        # DECLARE
        #   v_sync SYSTEXTIL.PCPC_040.FO2_TUSSOR_SYNC%TYPE;
        # BEGIN
        #   SELECT SYSTEXTIL.FO2_TUSSOR.nextval INTO v_sync FROM DUAL;
        #   IF INSERTING OR :old.FO2_TUSSOR_ID IS NULL THEN
        #     :new.FO2_TUSSOR_ID := v_sync;
        #   ELSE
        #     :new.FO2_TUSSOR_ID := :old.FO2_TUSSOR_ID;
        #   END IF;
        #   :new.FO2_TUSSOR_SYNC := v_sync;
        # END TUSSOR_TR_PCPC_040_SYNC

        # CREATE OR REPLACE TRIGGER SYSTEXTIL.TUSSOR_TR_PCPC_040_SYNC_DEL
        #   AFTER DELETE 
        #   ON SYSTEXTIL.PCPC_040
        #   FOR EACH ROW
        # BEGIN
        #   INSERT INTO FO2_TUSSOR_SYNC_DEL (TABELA, SYNC_ID)
        #   VALUES ('PCPC_040', :old.FO2_TUSSOR_ID);
        # END TUSSOR_TR_PCPC_040_SYNC_DEL

        self.tem_trigger = self.verifica_trigger()
        self.my_println(
            'Tabelas tem triggers'
            if self.tem_trigger
            else 'Tabelas não tem triggers'
        )

    def syncing(self):
        # pega no Systêxtil a lista OPs com um valor de teste de quantidade
        ics = self.get_ops_trail_s()

        # pega no Fo2 a lista OPs com um valor de teste de quantidade
        icf = self.get_ops_trail_f()

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
                self.my_println('Incluir OP {}'.format(op_s))
                self.inclui_op.append(op_s)
                count_task += 1
            elif op_s > op_f:
                self.my_println('Excluir OP {}'.format(op_f))
                self.exclui_op.append(op_f)
            else:
                if row_s['trail'] != row_f['trail']:
                    self.my_println('Atualizar OP {}'.format(op_f))
                    self.atualiza_op.append(op_s)
                    count_task += 1

        self.exec_tasks()

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        self.oponly = options['op']
        self.opini = options['opini']

        try:
            self.verificacoes()
            if self.tem_trigger and self.tem_col_sync:
                self.syncing()
        except Exception as e:
            raise CommandError('Error syncing lotes "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
