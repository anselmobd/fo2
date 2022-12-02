from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views.o2.get_post import O2BaseGetPostView

import lotes.forms as forms
import lotes.queries.lote
import lotes.queries.op
from lotes.queries.lote import get_per_oc


class CorrigeSequenciamento(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self):
        super(CorrigeSequenciamento, self).__init__()
        self.permission_required = 'lotes.can_repair_seq_op'
        self.Form_class = forms.OpForm
        self.template_name = 'lotes/corrige_sequenciamento.html'
        self.title_name = 'Corrige sequenciamento de lotes de OP'
        self.cleaned_data2self = True

    def mount_context(self):
        self.context.update({
            'op': self.op
        })

        cursor = db_cursor_so(self.request)

        data = get_per_oc.query(cursor, self.op)
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Sem lotes',
            })
            return

        exec = 'repair' in self.request.POST.keys()

        count_repair = 0
        for row in data:
            ret, alt, ests = lotes.queries.op.repair_sequencia_estagio(
                cursor, row['PERIODO'], row['OC'], exec)
            if ret:
                if exec:
                    row['INFO'] = 'Reparado'
                else:
                    row['INFO'] = 'Reparar'
                    count_repair += 1
            else:
                row['INFO'] = 'OK'
            row['ALT'] = alt
            row['ESTS'] = ests

        self.context.update({
            'count_repair': count_repair,
            'headers': ['Período', 'OC', 'Estágios', 'Informação',
                        'Alteração'],
            'fields': ['PERIODO', 'OC', 'ESTS', 'INFO',
                       'ALT'],
            'data': data,
        })

    # def start(self, request):
    #     self.request = request
    #     self.context = {'titulo': self.title_name}

    # def end(self):
    #     self.context['form'] = self.form
    #     return render(self.request, self.template_name, self.context)

    # def get(self, request, *args, **kwargs):
    #     self.start(request)
    #     self.form = self.Form_class()
    #     return self.end()

    # def post(self, request, *args, **kwargs):
    #     self.start(request)
    #     self.form = self.Form_class(self.request.POST)
    #     if self.form.is_valid():
    #         self.mount_context()
    #     return self.end()
