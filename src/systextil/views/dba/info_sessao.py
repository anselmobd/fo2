import sqlparse
from pprint import pprint

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)

from base.views import O2BaseGetPostView
from fo2.connections import db_cursor_so
from utils.functions.sql import sql_formato_fo2

from systextil.forms import SessaoForm
from systextil.queries.dba.main import get_info_sessao


class InfoSessao(LoginRequiredMixin, PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(InfoSessao, self).__init__(*args, **kwargs)
        self.permission_required = 'systextil.can_be_dba'
        self.template_name = 'systextil/dba/info_sessao.html'
        self.title_name = 'Informação sobre sessão'
        self.Form_class = SessaoForm
        self.form_class_initial = True
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = get_info_sessao(cursor, self.sessao_id)

        for row in data:
            row['id_serial'] = f"{row['sid']},{row['serial']}"

        self.context.update({
            'headers': [
                'Username', 'Módulo ', 'Status', 'Logon',
                'Última execução', 'ID,Serial', 'Máquina', 'Informação'
            ],
            'fields': [
                'username', 'module', 'status', 'logon_time',
                'prev_exec_start', 'id_serial', 'machine', 'client_info'
            ],
            'data': data,
        })
