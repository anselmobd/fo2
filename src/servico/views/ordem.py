from pprint import pprint

from django.db.models import Q

from base.views import O2BaseGetPostView
from utils.classes import LoggedInUser

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
            'equipe__id',
            'descricao',
        )

        if logged_in.user:
            try:
                usuario_funcao = servico.models.UsuarioFuncao.objects.get(
                    usuario=logged_in.user,
                    funcao__independente=False,
                    equipe=interacoes[0]['equipe__id']
                )
                nivel_op = usuario_funcao.funcao.nivel_operacional
            except servico.models.UsuarioFuncao.DoesNotExist:
                nivel_op = 0

            acesso = logged_in.user == doc.user
            if not acesso:
                try:
                    usuario_funcao = servico.models.UsuarioFuncao.objects.get(
                        usuario=logged_in.user,
                        funcao__independente=True,
                    )
                    acesso = True
                except servico.models.UsuarioFuncao.DoesNotExist:
                    pass

            self.tipos_eventos = servico.models.Evento.objects.filter(
                statusevento__status_pre=interacoes[0]['status_id']
            )
            if nivel_op > 0 and acesso:
                self.tipos_eventos = self.tipos_eventos.filter(
                    Q(nivel_op_minimo__gt=0, nivel_op_minimo__lte=nivel_op)
                    |
                    Q(nivel_op_minimo=0)
                )
            elif nivel_op > 0:
                self.tipos_eventos = self.tipos_eventos.filter(
                    nivel_op_minimo__gt=0, nivel_op_minimo__lte=nivel_op
                )
            elif acesso:
                self.tipos_eventos = self.tipos_eventos.filter(
                    nivel_op_minimo=0
                )
            else:
                # força não encontrar nada
                self.tipos_eventos = self.tipos_eventos.filter(
                    id=-1
                )
            self.tipos_eventos = self.tipos_eventos.order_by('ordem').values()
        else:
            self.tipos_eventos = []
        

        self.context.update({
            'interacoes': interacoes,
            'tipos_eventos': self.tipos_eventos,
        })