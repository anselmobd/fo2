from pprint import pprint

from base.views import O2BaseGetPostView
from utils.classes import LoggedInUser

import servico.forms
import servico.models
from servico.models.functions import get_eventos_possiveis


class Ordem(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Ordem, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = servico.forms.OrdemForm
        self.template_name = 'servico/ordem.html'
        self.title_name = 'Ordem'
        self.get_args = ['documento']


    def mount_context(self):
        logged_in = LoggedInUser()

        try:
            self.documento = int(self.documento)
            doc = servico.models.Documento.objects.get(id=self.documento)
            interacoes = servico.models.Interacao.objects.filter(documento=doc).order_by('-create_at')
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

        interacoes = interacoes.values(
            'create_at',
            'evento__nome',
            'status_id',
            'status__nome',
            'user__username',
            'classificacao__nome',
            'classificacao__horas',
            'equipe__nome',
            'equipe_id',
            'descricao',
        )

        if logged_in.user:
            self.tipos_eventos = get_eventos_possiveis(
                logged_in.user, doc, interacoes[0]['equipe_id'], interacoes[0]['status_id'])
        else:
            self.tipos_eventos = []
        

        self.context.update({
            'interacoes': interacoes,
            'tipos_eventos': self.tipos_eventos,
        })
