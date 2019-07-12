from django.views import View
from django.shortcuts import render

from base.views import O2BaseGetView

import manutencao.models as models


def index(request):
    context = {}
    return render(request, 'manutencao/index.html', context)


class Rotinas(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Rotinas, self).__init__(*args, **kwargs)
        self.template_name = 'manutencao/rotinas.html'
        self.title_name = 'Rotinas'

    def mount_context(self):
        rotinas = models.Rotina.objects.all().order_by(
            'tipo_maquina', 'nome')
        if len(rotinas) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma rotina cadastrada',
            })
            return

        data = list(rotinas.values('tipo_maquina__nome', 'nome'))

        self.context.update({
            'headers': ('Tipo de máquina', 'Nome da rotina'),
            'fields': ('tipo_maquina__nome', 'nome'),
            'data': data,
        })
