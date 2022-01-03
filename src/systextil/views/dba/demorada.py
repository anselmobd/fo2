import sqlparse
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from base.views import O2BaseGetPostView
from fo2.connections import db_cursor_so
from utils.functions.sql import sql_formato_fo2

from systextil.forms import SegundosForm
from systextil.queries.dba.main import rodando_a_segundos


class Demorada(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Demorada, self).__init__(*args, **kwargs)
        self.permission_required = 'systextil.can_be_dba'
        self.template_name = 'systextil/dba/demorada.html'
        self.title_name = 'Queries Demoradas'
        self.Form_class = SegundosForm
        self.form_class_initial = True
        self.cleaned_data2self = True
        self.get_args = ['segundos']

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
            'segundos': self.segundos,
            'headers': ['Username', 'SID', 'Serial', 'Tempo', 'SQL'],
            'data': data,
        })
