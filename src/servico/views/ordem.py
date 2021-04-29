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
        self.get_args = ['documento']


    def mount_context(self):
        try:
            self.documento = int(self.documento)
            doc = servico.models.Documento.objects.get(id=self.documento)
            eventos = servico.models.Interacao.objects.filter(documento=doc).order_by('-create_at')
        except servico.models.Documento.DoesNotExist:
            self.context.update({
                'erro': 'Ordem não encontrada.',
            })
            return

        self.context.update({
            'documento': doc.id,
            'usuario': doc.user.username,
            'data': doc.create_at,
            'ativo': doc.ativo,
        })
        if not doc.ativo:
            return

        eventos = eventos.values(
            'create_at',
            'evento__nome',
            'status_id',
            'status__nome',
            'user__username',
            'nivel__nome',
            'equipe__nome',
            'descricao',
        )

        self.tipos_eventos = servico.models.Evento.objects.filter(
            statusevento__status_pre=eventos[0]['status_id']).order_by('ordem')

        self.context.update({
            'eventos': eventos,
            'tipos_eventos': self.tipos_eventos,
        })