from pprint import pprint

from base.views import O2BaseGetPostView

import servico.forms
import servico.models


class Ordem(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Ordem, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = servico.forms.OrdemForm
        self.template_name = 'servico/ordem.html'
        self.title_name = 'Ordem'


    def mount_context(self):
        try:
            self.ordem = int(self.ordem)
            doc = servico.models.NumeroDocumento.objects.get(id=self.ordem)
            data = servico.models.ServicoEvento.objects.filter(numero=doc)
        except servico.models.NumeroDocumento.DoesNotExist:
            self.context.update({
                'erro': 'Ordem não encontrada.',
            })
            return
