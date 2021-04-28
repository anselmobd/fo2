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

from utils.functions.models import queryset_to_dict_list_lower

from base.pages_context import get_current_users_requisicao


class O2BaseGetPostView(CustomView):

    def __init__(self, *args, **kwargs):
        """
        Inicializa parâmetros, sendo:
        
        cleaned_data2self
            valores no self.form.cleaned_data viram atributos do objeto (self)
        """
        super(O2BaseGetPostView, self).__init__(*args, **kwargs)
        self.cleaned_data2self = False

    def do_cleaned_data2self(self):
        if self.cleaned_data2self:
            for field in self.form.cleaned_data:
                setattr(self, field, self.form.cleaned_data[field])

    def render_mount(self):
        self.pre_mount_context()
        if self.form.is_valid():
            self.do_cleaned_data2self()
            self.mount_context()
        self.context['form'] = self.form
        return self.my_render()

    def set_form_arg(self, field):
        value = self.get_arg(field)
        if value is not None:
            self.form.data[field] = value

    def empty_form_initial(self):
        """Monta um dict com campos do Form_class e valores None"""
        return {name: None for name in self.Form_class.base_fields}

    def form_initial(self):
        """Metodo chamado no GET para colocar valores no dict que inicializará o Form_class"""
        return self.empty_form_initial()

    def pre_form(self):
        pass

    def get(self, request, *args, **kwargs):
        self.init_self(request, kwargs)
        if self.get_args2form:
            for arg in self.get_args:
                if self.get_arg(arg) is not None:
                    return self.post(request, *args, **kwargs)

        self.pre_form()
        self.form = self.Form_class(initial=self.form_initial())
        return self.render_mount()

    def post(self, request, *args, **kwargs):
        self.init_self(request, kwargs)
        self.form = self.Form_class(self.request.POST)

        if self.get_args2form:
            for arg in self.get_args:
                self.set_form_arg(arg)

        return self.render_mount()


class O2BaseGetView(CustomView):

    def render_mount(self):
        self.mount_context()
        return self.my_render()

    def get(self, request, *args, **kwargs):
        self.init_self(request, kwargs)

        return self.render_mount()


def index(request):
    return render(request, 'base/index.html')


class Usuarios(PermissionRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Usuarios, self).__init__(*args, **kwargs)
        self.permission_required = 'base.can_visualize_usage_log'
        self.template_name = 'base/usuarios.html'
        self.title_name = 'Usuários conectados'

    def mount_context(self):
        queryset = get_current_users_requisicao()

        data = queryset_to_dict_list_lower(
            queryset.filter(ip_interno=True).order_by('nome'))
        self.context.update({
            'headers': ['Nome', 'Último login', 'Última ação'],
            'fields': ['nome', 'quando', 'ult_acao'],
            'data': data,
        })

        r_data = queryset_to_dict_list_lower(
            queryset.filter(ip_interno=False).order_by('nome'))
        self.context.update({
            'r_headers': ['Nome', 'Último login', 'Última ação'],
            'r_fields': ['nome', 'quando', 'ult_acao'],
            'r_data': r_data,
        })


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
        try:
            db_dict = databases[db_id]

            dsn_tns = cx_Oracle.makedsn(
                db_dict['HOST'],
                db_dict['PORT'],
                service_name=db_dict['NAME'],
            )

            conn = cx_Oracle.connect(
                user=db_dict['USER'],
                password=db_dict['PASSWORD'],
                dsn=dsn_tns
            )

            cursor = conn.cursor()

            conn.close()

            self.context['msgs_ok'].append(f'Banco "{db_id}" acessível')
            return True

        except Exception as e:
            self.context['msgs_erro'].append(
                f'Erro ao acessar banco "{db_id}" [{e}]')
            return False

    def mount_context(self):
        self.context.update({
            'msgs_ok': [],
            'msgs_erro': [],
        })

        self.acessa_oracle_db(settings.DATABASES, 'so')
        self.acessa_oracle_db(settings.DATABASES_EXTRAS, 'sh')
        self.acessa_fdb_db(settings.DATABASES_EXTRAS, 'f1')
