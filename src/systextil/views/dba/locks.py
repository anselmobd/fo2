import sqlparse
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from o2.views.base.get import O2BaseGetView
from fo2.connections import db_cursor_so
from utils.functions.sql import sql_formato_fo2

from systextil.queries.dba import locks


class Locks(PermissionRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Locks, self).__init__(*args, **kwargs)
        self.permission_required = 'systextil.can_be_dba'
        self.template_name = 'systextil/dba/locks.html'
        self.title_name = 'Locks'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        raw_data = locks.query(cursor)

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
            row['sql_text_parse'] = sqlparse.format(
                row['sql_text'],
                reindent_aligned=True,
                indent_width=2,
                keyword_case='upper',
            )
            row['sql_text_fo2'] = sql_formato_fo2(row['sql_text'])

        self.context.update({
            'headers': [
                'Audit Sid',
                'Sid',
                'Serial',
                'Minutos',
                'Program',
                'Module',
                'Action',
                'Process',
                'Lock Held',
                'Lock Requested',
                'Lock Type',
                'Objeto',
                'SQL'
            ],
            'data': data,
        })
