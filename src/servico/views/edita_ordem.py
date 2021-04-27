from pprint import pprint

from django import forms
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
        self.Form_class = servico.forms.CriaInteracaoForm
        self.template_name = 'servico/edita_ordem.html'
        self.title_name = 'Edita ordem'
        self.get_args = ['evento', 'documento']


    def get_records(self):
        try:
            self.tipo_record = servico.models.TipoDocumento.objects.get(slug='os')
        except servico.models.TipoDocumento.DoesNotExist as e:
            self.context.update({
                'preerro': 'Tipo de documento inválido.',
            })
            raise e

        try:
            self.doc = servico.models.Documento.objects.get(id=self.context['documento'])
        except Exception as e:
            self.context.update({
                'preerro': 'Número de documento não encontrado.',
            })
            raise e

        try:
            last_interacao = servico.models.Interacao.objects.filter(
                documento=self.doc).order_by('create_at').last()
        except Exception as e:
            self.context.update({
                'preerro': f'Não foi possível pegar última interação.',
            })
            raise e

        try:
            self.evento_record = servico.models.Evento.objects.get(
                codigo=self.context['evento'], statusevento__status_pre=last_interacao.status)
        except servico.models.Evento.DoesNotExist as e:
            self.context.update({
                'preerro': 'Evento inválido.',
            })
            raise e

    def pre_mount_context(self):
        try:
            self.context['documento'] = int(self.context['documento'])
            self.get_records()
        except Exception:
            return
        self.context.update({
            'evento_record': self.evento_record,
        })
        if not self.evento_record.edita_nivel:
            self.form.fields['nivel'].widget = forms.HiddenInput()
            self.form.fields['nivel'].required = False
        if not self.evento_record.edita_equipe:
            self.form.fields['equipe'].widget = forms.HiddenInput()
            self.form.fields['equipe'].required = False
        if not self.evento_record.edita_descricao:
            self.form.fields['descricao'].widget = forms.HiddenInput()
            self.form.fields['descricao'].required = False

    def mount_context(self):
        try:
            msg = {}
            with transaction.atomic():
                # self.salva_evento()
                self.doc = salva_interacao(
                    msg, self.request, 
                    nivel=self.nivel,
                    equipe=self.equipe,
                    descricao=self.descricao,
                )
        except Exception:
            self.context.update(msg)
            return
        doc_num = self.doc.id
        self.redirect = ('servico:ordem__get', doc_num)
