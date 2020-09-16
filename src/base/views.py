import cx_Oracle
from pprint import pprint

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

from utils.functions.models import queryset_to_dict_list_lower

from base.pages_context import get_current_users_requisicao


class O2BaseCustomView(View):

    def __init__(self):
        self.get_args = []
        self.get_args2context = False

    def init_self(self, request, kwargs):
        self.request = request
        self.kwargs = kwargs

        self.context = {}
        if hasattr(self, 'title_name'):
            self.context.update({'titulo': self.title_name})

        if self.get_args2context:
            for arg in self.get_args:
                arg_value = self.get_arg(arg)
                self.context.update({arg: arg_value})

    def get_arg(self, field):
        return self.kwargs[field] if field in self.kwargs else None

    def my_render(self):
        return render(self.request, self.template_name, self.context)

    def mount_context(self):
        pass


class O2BaseGetPostView(O2BaseCustomView):

    def render_mount(self):
        if self.form.is_valid():
            self.mount_context()
        self.context['form'] = self.form
        return self.my_render()

    def set_form_arg(self, field):
        value = self.get_arg(field)
        if value is not None:
            self.form.data[field] = value

    def get(self, request, *args, **kwargs):
        self.init_self(request, kwargs)

        for arg in self.get_args:
            if self.get_arg(arg) is not None:
                return self.post(request, *args, **kwargs)

        self.form = self.Form_class()
        return self.render_mount()

    def post(self, request, *args, **kwargs):
        self.init_self(request, kwargs)
        self.form = self.Form_class(self.request.POST)

        for arg in self.get_args:
            self.set_form_arg(arg)

        return self.render_mount()


class O2BaseGetView(O2BaseCustomView):

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

            conn.close()

            self.context['msgs_ok'].append(f'Banco "{db_id}" acessível')

        except Exception as e:
            self.context['msgs_erro'].append(
                f'Erro ao acessar banco "{db_id}" [{e}]')

    def mount_context(self):
        self.context.update({
            'msgs_ok': [],
            'msgs_erro': [],
        })

        self.acessa_oracle_db(settings.DATABASES, 'so')
        self.acessa_oracle_db(settings.DATABASES_EXTRAS, 'sh')
