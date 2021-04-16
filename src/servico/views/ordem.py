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
            eventos = servico.models.ServicoEvento.objects.filter(numero=doc).order_by('create_at')
        except servico.models.NumeroDocumento.DoesNotExist:
            self.context.update({
                'erro': 'Ordem não encontrada.',
            })
            return

        self.context.update({
            'numero': doc.id,
            'usuario': doc.user.username,
            'data': doc.create_at,
            'ativo': doc.ativo,
        })
        if not doc.ativo:
            return

        eventos = eventos.values(
            'user__username',
            'create_at',
            'evento__nome',
            'nivel__nome',
            'equipe__nome',
            'descricao',
        )
        self.context.update({
            'eventos': eventos,
        })