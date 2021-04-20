from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.db.utils import Error

from base.views import O2BaseGetPostView
from o2.functions import csrf_used

import servico.forms
import servico.models


class CriaOrdem(LoginRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(CriaOrdem, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = servico.forms.CriaServicoEventoForm
        self.template_name = 'servico/cria_ordem.html'
        self.title_name = 'Cria ordem'


    def salva_evento(self):
        if csrf_used(self.request):
            self.context.update({
                'erro': 'Formulário já gravado.',
            })
            raise Error

        try:
            tipo = servico.models.TipoDocumento.objects.get(slug='os')
        except servico.models.TipoDocumento.DoesNotExist as e:
            self.context.update({
                'erro': 'Tipo de documento inválido.',
            })
            raise e

        try:
            evento = servico.models.TipoEvento.objects.get(slug='req')
        except servico.models.TipoEvento.DoesNotExist as e:
            self.context.update({
                'erro': 'Tipo de evento inválido.',
            })
            raise e

        try:
            self.doc = servico.models.NumeroDocumento(tipo=tipo)
            self.doc.save()
        except Exception as e:
            self.context.update({
                'erro': 'Não foi possível gerar um número de documento.',
            })
            raise e

        try:
            evento = servico.models.ServicoEvento(
                numero=self.doc,
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
            raise e

        self.doc.ativo = True
        self.doc.save()


    def mount_context(self):
        try:
            with transaction.atomic():
                self.salva_evento()
        except Exception:
            return
        numero = self.doc.id
        self.redirect = ('servico:ordem__get', numero)
