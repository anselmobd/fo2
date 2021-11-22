from pprint import pprint

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)

from base.views import O2BaseGetPostView
from fo2.connections import db_cursor_so

from systextil.forms import SegundosForm
from systextil.queries.dba.main import rodando_a_segundos

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

        data = rodando_a_segundos(cursor,self.segundos)

        for row in data:
            mins = row['secs'] // 60
            secs = row['secs'] % 60
            row['secs'] = f"{mins}:{secs:02d}"

        self.context.update({
            'headers': ['Username', 'SID', 'Serial#', 'Rodando a', 'SQL'],
            'fields': ['username', 'sid', 'serial#', 'secs', 'sql_text'],
            'data': data,
        })
