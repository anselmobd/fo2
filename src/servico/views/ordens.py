from pprint import pprint

from base.views import O2BaseGetPostView

import servico.forms
import servico.models


class Ordens(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Ordens, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = servico.forms.OrdensForm
        self.template_name = 'servico/ordens.html'
        self.title_name = 'Ordens'


    def mount_context(self):
        try:
            self.ordem = int(self.ordem)
        except Exception:
            return
        
        if self.ordem == 0:
            data = servico.models.ServicoEvento.objects.all()
        else:
            try:
                doc = servico.models.NumeroDocumento.objects.get(id=self.ordem)
                data = servico.models.ServicoEvento.objects.filter(numero=doc)
            except servico.models.NumeroDocumento.DoesNotExist:
                self.context.update({
                    'erro': 'Ordem não encontrada.',
                })
                return

        data = data.values(
            'numero_id', 'create_at', 'user__username', 'descricao', 'equipe__nome', 'evento__nome', 'nivel__nome'
        )

        self.context.update({
            'headers': ['Número', 'Evento', 'Data/hora', 'Usuário', 'Descrição', 'Equipe', 'Nível'],
            'fields': ['numero_id', 'evento__nome', 'create_at', 'user__username', 'descricao', 'equipe__nome', 'nivel__nome'],
            'data': data,
        })
