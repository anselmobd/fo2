from pprint import pprint

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.urls import reverse

from base.views import O2BaseGetView
from fo2.connections import db_cursor_so

from systextil.queries.dba.main import sessoes_travadoras


class Travadora(LoginRequiredMixin, PermissionRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Travadora, self).__init__(*args, **kwargs)
        self.permission_required = 'systextil.can_be_dba'
        self.template_name = 'systextil/dba/travadora.html'
        self.title_name = 'Sessões travadoras'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = sessoes_travadoras(cursor)

        for row in data:
            row['sessao_travadora|LINK'] = reverse(
                'systextil:info_sessao__get',
                args=[row['sessao_travadora']]
            )
            row['sessao_travadora|TARGET'] = '_blank'

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
