import sqlparse
from pprint import pprint

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)

from base.views import O2BaseGetPostView, O2BaseGetView
from fo2.connections import db_cursor_so
from utils.functions.sql import sql_formato_fo2

from systextil.forms import SegundosForm
from systextil.queries.dba.main import rodando_a_segundos, sessoes_travadoras


class Demorada(LoginRequiredMixin, PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Demorada, self).__init__(*args, **kwargs)
        self.permission_required = 'systextil.can_be_dba'
        self.template_name = 'systextil/dba/demorada.html'
        self.title_name = 'Queries Demoradas'
        self.Form_class = SegundosForm
        self.form_class_initial = True
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        raw_data = rodando_a_segundos(cursor, self.segundos)

        data = []
        last_sid = -1
        last_serial = -1
        for row in raw_data:
            if row['sid'] == last_sid and row['serial'] == last_serial:
                data[-1]['sql_text'] += row['sql_text']
            else:
                data.append(row)                
                last_sid = row['sid']
                last_serial = row['serial']

        for row in data:
            mins = row['secs'] // 60
            secs = row['secs'] % 60
            row['mins'] = f"{mins}:{secs:02d}"
            row['serial'] = f"{row['serial']:d}"
            row['sql_text_parse'] = sqlparse.format(
                row['sql_text'],
                reindent_aligned=True,
                indent_width=2,
                keyword_case='upper',
            )
            row['sql_text_fo2'] = sql_formato_fo2(row['sql_text'])

        self.context.update({
            'headers': ['Username', 'SID', 'Serial', 'Tempo', 'SQL'],
            'data': data,
        })


class Travadora(LoginRequiredMixin, PermissionRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Travadora, self).__init__(*args, **kwargs)
        self.permission_required = 'systextil.can_be_dba'
        self.template_name = 'systextil/dba/travadora.html'
        self.title_name = 'Sessões travadoras'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = sessoes_travadoras(cursor)

        self.context.update({
            'headers': [
                'Sessão Travadora',
                'Usuário Travador ',
                'Sessão Esperando',
                'Usuário Esperando',
                'Lock type',
                'Mode held',
                'Mode requested',
                'Lock id1',
                'Lock id2',
            ],
            'fields': [
                'sessao_travadora',
                'usuario_travador',
                'sessao_esperando',
                'usuario_esperando',
                'lock_type',
                'mode_held',
                'mode_requested',
                'lock_id1',
                'lock_id2',
            ],
            'data': data,
        })
