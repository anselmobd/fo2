import cx_Oracle
# import firebirdsql
import fdb
# from firebird.base import DatabaseWrapper
import time
from pprint import pprint

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

from o2.views.base.custom import CustomView

from utils.functions.models.dictlist import queryset_to_dictlist_lower
from utils.functions.oracle import get_oracle_conn_err

from base.pages_context import get_current_users_requisicao
from o2.views.base.get import O2BaseGetView


def index(request):
    return render(request, 'base/index.html')


class TestaDB(PermissionRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(TestaDB, self).__init__(*args, **kwargs)
        self.permission_required = 'base.can_visualize_usage_log'
        self.template_name = 'base/testa_db.html'
        self.title_name = 'Testa banco de dados'

    def connect_fdb(self, databases, db_id, return_error=False):
        try:
            db_dict = databases[db_id]

            conn = fdb.connect(
                host=db_dict['HOST'],
                port=db_dict['PORT'],
                database=db_dict['NAME'],
                user=db_dict['USER'],
                password=db_dict['PASSWORD'],
                sql_dialect=db_dict['DIALECT'],
                charset=db_dict['OPTIONS']['charset'],
            )
            return conn

        except Exception as e:
            if return_error:
                return e
            else:
                raise e

    def conecta_fdb_db(self, databases, db_id):
        conn = self.connect_fdb(databases, db_id, return_error=True)

        if isinstance(conn, Exception):
            return False, conn
        else:
            try:
                cursor = conn.cursor()
                conn.close()
                return True, None
            except Exception as e:
                return False, e

    def acessa_fdb_db(self, databases, db_id):
        count = 0

        while count < 20:
            result, e = self.conecta_fdb_db(databases, db_id)
            if result:
                self.context['msgs_ok'].append(f'Banco "{db_id}" acessível')
                break
            else:
                error = e
            count += 1
            time.sleep(0.5)

        if count != 0:
            self.context['msgs_erro'].append(
                f'({count}) Erro ao acessar banco "{db_id}" [{error}]')

    def acessa_oracle_db(self, databases, db_id):
        connect_dict = databases[db_id] if db_id in databases else {}
        conn, err = get_oracle_conn_err(**connect_dict)
        if conn:
            try:
                cursor = conn.cursor()
                conn.close()
            except Exception as e:
                conn = None
                err = e

        if conn:
            self.context['msgs_ok'].append(f'Banco "{db_id}" acessível')
            return True
        else:
            self.context['msgs_erro'].append(
                f'Erro ao acessar banco "{db_id}" [{err}]')
            return False

    def mount_context(self):
        self.context.update({
            'msgs_ok': [],
            'msgs_erro': [],
        })

        self.acessa_oracle_db(settings.DATABASES, 'so')
        self.acessa_oracle_db(settings.DATABASES_EXTRAS, 'sn')
        self.acessa_oracle_db(settings.DATABASES_EXTRAS, 'sh')
        self.acessa_fdb_db(settings.DATABASES_EXTRAS, 'f1')
