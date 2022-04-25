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
from utils.functions.oracle import get_oracle_conn_err

from base.pages_context import get_current_users_requisicao


class O2BaseGetPostView(CustomView):
    """Classe base para uma view com GET e POST
    
    Obrigatório definir no __init__:
        Form_class <django.forms.Form>
    """

    def __init__(self, *args, **kwargs):
        """Inicializa parâmetros, sendo:
        
        cleaned_data2self
            valores no self.form.cleaned_data viram atributos do objeto (self)
        """
        super(O2BaseGetPostView, self).__init__(*args, **kwargs)
        self.Form_class = None
        self.form_class_has_initial = False
        self.form_dict_initial = {}
        self.form_create_kwargs = {}
        self.cleaned_data2self = False
        self.cleaned_data2data = False

    def do_cleaned_data2self(self):
        if self.cleaned_data2self:
            for field in self.form.cleaned_data:
                setattr(self, field, self.form.cleaned_data[field])

    def do_cleaned_data2data(self):
        if self.cleaned_data2data:
            self.form.data = dict(self.form.data)
            for field in self.form.cleaned_data:
                self.form.data[field] = self.form.cleaned_data[field]

    def render_mount(self):
        self.pre_mount_context()
        if self.form.is_valid():
            self.do_cleaned_data2self()
            self.do_cleaned_data2data()
            self.mount_context()
        self.context['form'] = self.form
        return self.my_render()

    def set_form_arg(self, field):
        value = self.get_arg(field)
        if value is not None:

            # evita erro "This QueryDict instance is immutable"
            aux_data = self.form.data.copy()
            self.form.data = aux_data

            self.form.data[field] = value

    def empty_form_initial(self):
        """Monta um dict com campos do Form_class e valores None"""
        return {name: None for name in self.Form_class.base_fields}

    def form_initial(self):
        """Metodo chamado no GET para colocar valores no dict que inicializará o Form_class"""
        empty_dict_initial = self.empty_form_initial()
        empty_dict_initial.update(self.form_dict_initial)
        return empty_dict_initial

    def pre_form(self):
        pass

    def get(self, request, *args, **kwargs):
        self.init_self(request, kwargs)
        if self.get_args2form:
            for arg in self.get_args:
                if self.get_arg(arg) is not None:
                    return self.post(request, *args, **kwargs)

        self.pre_form()
        if self.form_class_has_initial:
            self.form = self.Form_class(**self.form_create_kwargs)
        else:
            self.form = self.Form_class(
                initial=self.form_initial(), **self.form_create_kwargs)
        return self.render_mount()

    def post(self, request, *args, **kwargs):
        self.init_self(request, kwargs)
        self.pre_form()
        self.form = self.Form_class(self.request.POST, **self.form_create_kwargs)

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
