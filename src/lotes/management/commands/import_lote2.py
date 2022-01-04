import datetime
import sys
from pprint import pformat, pprint

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import Max

from fo2.connections import db_cursor_so

from utils.functions.models import rows_to_dict_list_lower

import base.models
import lotes.models


class Command(BaseCommand):
    help = 'Syncronizing Lotes (versão 2)'
    __MAX_TASKS = 5

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

    def get_lotes_to_sync(self):
        sql = f"""
            WITH SYNCS AS
            ( SELECT
                le.FO2_TUSSOR_SYNC
              FROM PCPC_040 le -- lote estágio
              WHERE 1=1
                AND le.FO2_TUSSOR_SYNC > {self.last_sync}
              ORDER BY
                le.FO2_TUSSOR_SYNC
            )
            , FIRSTS AS
            ( SELECT
                *
              FROM SYNCS le -- lote estágio
              WHERE rownum <= {self.__MAX_TASKS}
            )
            , ULT AS
            ( SELECT 
                le.ORDEM_PRODUCAO OP
              , max(le.CODIGO_ESTAGIO) ULTIMO_ESTAGIO
              , max(le.SEQUENCIA_ESTAGIO) ULTIMA_SEQ_ESTAGIO
              FROM PCPC_040 le -- lote estágio
              GROUP BY
                le.ORDEM_PRODUCAO
            )
            , LOTES AS
            ( SELECT
                u.OP
              , le.PERIODO_PRODUCAO PERIODO
              , le.ORDEM_CONFECCAO OC
              , le.PROCONF_GRUPO REF
              , le.PROCONF_SUBGRUPO TAM
              , t.ORDEM_TAMANHO ORD_TAM
              , le.PROCONF_ITEM COR
              , le.QTDE_PECAS_PROG QTD_PRODUZIR
              , u.ULTIMO_ESTAGIO
              , u.ULTIMA_SEQ_ESTAGIO
              , s.FO2_TUSSOR_SYNC
              FROM PCPC_040 le -- lote estágio
              JOIN FIRSTS s
                ON s.FO2_TUSSOR_SYNC = le.FO2_TUSSOR_SYNC
              JOIN ULT u
                ON u.OP = le.ORDEM_PRODUCAO
              LEFT JOIN BASI_220 t
                ON t.TAMANHO_REF = le.PROCONF_SUBGRUPO
              WHERE 1=1
                AND le.QTDE_PECAS_PROG IS NOT NULL
                AND le.QTDE_PECAS_PROG <> 0
              ORDER BY
                le.FO2_TUSSOR_SYNC
            )
            , OCS AS
            ( SELECT
                lote.OP
              , lote.PERIODO
              , lote.OC
              , lote.REF
              , lote.TAM
              , lote.ORD_TAM
              , lote.COR
              , lote.QTD_PRODUZIR
              , CASE WHEN l.ORDEM_CONFECCAO IS NULL THEN 999
                ELSE l.CODIGO_ESTAGIO END ESTAGIO
              , CASE WHEN l.ORDEM_CONFECCAO IS NULL THEN lf.QTDE_PECAS_PROD
                ELSE l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO END QTD
              , CASE WHEN l.ORDEM_CONFECCAO IS NULL THEN 0
                ELSE l.QTDE_CONSERTO END CONSERTO
              , lote.FO2_TUSSOR_SYNC
              FROM LOTES lote
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
            )
            SELECT
              oc.*
            FROM OCS oc
        """
        self.my_println(sql)
        data = self.cursor_s.execute(sql)
        return rows_to_dict_list_lower(data)

    def get_lotes_to_del(self):
        sql = f"""
            WITH QUERY AS
            ( SELECT DISTINCT
                d.SYNC_ID DELETED_SYNC_ID
              FROM FO2_TUSSOR_SYNC_DEL d
              WHERE d.TABELA = 'PCPC_040'
                AND d.ID > {self.last_del_id}
              ORDER BY
                d.SYNC_ID
            )
            SELECT 
              *
            FROM QUERY q
            WHERE rownum <= {self.__MAX_TASKS}
        """
        data = self.cursor_s.execute(sql)
        return rows_to_dict_list_lower(data)

    def none_value(self, vari, value):
        return value if vari is None else vari

    def syncing(self):
        self.cursor_f = conn = connections['default'].cursor()
        self.cursor_s = db_cursor_so()

        try:
            self.table_obj = base.models.SyncDelTable.objects.get(nome='PCPC_040')
        except base.models.SyncDelTable.DoesNotExist:
            self.table_obj = base.models.SyncDelTable.objects.create(
                nome='PCPC_040',
            )

        # pega no Fo2 os últimos syncs
        self.last_sync = self.none_value(
            lotes.models.Lote.objects.aggregate(Max('sync'))['sync__max'],
            -1
        )
        self.my_println(f"last sync = {self.last_sync}")

        self.last_del_id = self.none_value(
            base.models.SyncDel.objects.filter(
                tabela=self.table_obj
            ).aggregate(Max('id'))['id__max'],
            -1
        )
        self.my_println(f"last del id  = {self.last_del_id}")

        # pega no Systêxtil lotes com sync mais recente
        self.lotes_to_sync = self.get_lotes_to_sync()
        self.my_pprintln(self.lotes_to_sync)

        # pega no Systêxtil lotes apagados com id mais recente
        self.lotes_to_del = self.get_lotes_to_del()
        self.my_pprintln(self.lotes_to_del)

        # count_task = 0
        # while count_task < self.__MAX_TASKS:
        #     break

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        try:
            self.syncing()
        except Exception as e:
            raise CommandError('Error syncing lotes "{}"'.format(e))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
