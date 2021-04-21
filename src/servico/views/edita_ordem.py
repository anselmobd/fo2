from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.db.utils import Error

from base.views import O2BaseGetPostView
from o2.functions import csrf_used

import servico.forms
import servico.models


class EditaOrdem(LoginRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(EditaOrdem, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.get_args2context = True
        self.get_args2form = False
        self.Form_class = servico.forms.CriaServicoEventoForm
        self.template_name = 'servico/edita_ordem.html'
        self.title_name = 'Edita ordem'
        self.get_args = ['evento', 'numero']


    def get_records(self):
        try:
            self.tipo_record = servico.models.TipoDocumento.objects.get(slug='os')
        except servico.models.TipoDocumento.DoesNotExist as e:
            self.context.update({
                'erro': 'Tipo de documento inválido.',
            })
            raise e

        try:
            self.evento_record = servico.models.Evento.objects.get(codigo=self.context['evento'])
        except servico.models.Evento.DoesNotExist as e:
            self.context.update({
                'erro': 'Evento inválido.',
            })
            raise e

        try:
            self.doc = servico.models.NumeroDocumento.objects.get(id=self.context['numero'])
        except Exception as e:
            self.context.update({
                'erro': 'Número de documento não encontrado.',
            })
            raise e

    def pre_mount_context(self):
        print('pre_mount_context')
        print(self.context['evento'])
        print(self.context['numero'])
        try:
            self.context['numero'] = int(self.context['numero'])
            self.get_records()
        except Exception:
            return
        self.context.update({
            'evento_record': self.evento_record,
        })

    def mount_context(self):
        pprint(self.tipo_record)
        pprint(self.evento_record)
        pprint(self.doc)
