from pprint import pprint

from base.views import O2BaseGetPostView

import servico.forms
import servico.models


class Lista(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Lista, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = servico.forms.ListaForm
        self.template_name = 'servico/lista.html'
        self.title_name = 'Lista ordens'


    def mount_context(self):
        try:
            self.ordem = int(self.ordem)
        except Exception:
            return
        
        if self.ordem == 0:
            interacoes = servico.models.Interacao.objects.all().order_by(
                "-documento__id", "-create_at")
        else:
            try:
                interacoes = servico.models.Interacao.objects.filter(documento__id=self.ordem)
            except servico.models.Documento.DoesNotExist:
                self.context.update({
                    'erro': 'Ordem não encontrada.',
                })
                return

        interacoes = interacoes.values(
            'documento__id', 'create_at', 'user__username', 'descricao', 'equipe__nome', 'status__nome', 'evento__nome', 'nivel__nome'
        )

        self.context.update({
            'headers': ['#', 'Status', 'Evento', 'Usuário', 'Data/hora', 'Equipe', 'Descrição', 'Nível'],
            'fields': ['documento__id', 'status__nome', 'evento__nome', 'user__username', 'create_at', 'equipe__nome', 'descricao', 'nivel__nome'],
            'data': interacoes,
        })
