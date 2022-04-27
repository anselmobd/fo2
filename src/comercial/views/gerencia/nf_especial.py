from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

from contabil.queries import nf_inform

import comercial.forms
from comercial.queries.gerencia import nf_especial

class NfEspecial(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self):
        super(NfEspecial, self).__init__()
        self.permission_required = 'comercial.can_gerenciar_nf_especial'
        self.Form_class = comercial.forms.NfEspecialForm
        self.cleaned_data2self = True
        self.template_name = 'comercial/gerencia/nf_especial.html'
        self.title_name = 'NF especial'


    def mount_nfs_especiais(self):
        dados = nf_especial.get_nfs_especiais(self.cursor)
        self.context.update({
            'headers': [
                'NF',
                'Nível',
                'Referência',
                'Tamanho',
                'Cor',
            ],
            'fields': [
                'nf',
                'nivel',
                'ref',
                'tam',
                'cor',
            ],
            'data': dados,
        })

    def pre_mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.mount_nfs_especiais()

    def mount_context(self):
        self.context.update({
            'nf': self.nf,
        })

        data = nf_inform(self.cursor, self.nf, especiais=True)
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Nota fiscal não encontrada',
            })
            return

        mess_error = nf_especial.set_nf_especial(self.cursor, self.nf)

        if mess_error:
            self.context.update({
                'result': f'Erro: {mess_error}',
            })
            return

        self.mount_nfs_especiais()
        self.context.update({
            'result': 'OK',
        })
