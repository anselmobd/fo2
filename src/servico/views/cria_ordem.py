from pprint import pprint

from base.views import O2BaseGetPostView

import servico.forms
import servico.models


class CriaOrdem(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(CriaOrdem, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = servico.forms.CriaServicoEventoForm
        self.template_name = 'servico/cria_ordem.html'
        self.title_name = 'Cria ordem'


    def mount_context(self):
        try:
            tipo = servico.models.TipoDocumento.objects.get(slug='os')
        except servico.models.TipoDocumento.DoesNotExist:
            self.context.update({
                'erro': 'Tipo de documento inválido.',
            })
            return

        try:
            evento = servico.models.TipoEvento.objects.get(slug='req')
        except servico.models.TipoEvento.DoesNotExist:
            self.context.update({
                'erro': 'Tipo de evento inválido.',
            })
            return

        try:
            doc = servico.models.NumeroDocumento(tipo=tipo)
            doc.save()
        except Exception:
            self.context.update({
                'erro': 'Não foi possível gerar um número de documento.',
            })
            return

        pprint(self.__dict__)
        try:
            evento = servico.models.ServicoEvento(
                numero=doc,
                evento=evento,
                nivel=self.nivel,
                equipe=self.equipe,
                descricao=self.descricao,
            )
            evento.save()
        except Exception as e:
            self.context.update({
                'erro': 'Não foi possível gerar o evento de requisição.',
            })
            return
