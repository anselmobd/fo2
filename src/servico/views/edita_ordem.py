from pprint import pprint

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from base.views import O2BaseGetPostView

import servico.forms
import servico.models
from servico.views.cria_ordem import salva_interacao

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
            self.last_interacao = servico.models.Interacao.objects.filter(
                documento=self.doc).order_by('create_at').last()
        except Exception as e:
            self.context.update({
                'preerro': f'Não foi possível pegar última interação.',
            })
            raise e

        try:
            self.evento_record = servico.models.Evento.objects.get(
                codigo=self.context['evento'], statusevento__status_pre=self.last_interacao.status)
        except servico.models.Evento.DoesNotExist as e:
            self.context.update({
                'preerro': 'Evento inválido.',
            })
            raise e

    def pre_form(self):
        try:
            self.context['documento'] = int(self.context['documento'])
            self.get_records()
        except Exception:
            return
        self.context.update({
            'evento_record': self.evento_record,
        })

    def pre_mount_context(self):
        if not self.evento_record.edita_nivel:
            self.form.fields['classificacao'].widget = forms.HiddenInput()
            self.form.fields['classificacao'].required = False
        if not self.evento_record.edita_equipe:
            self.form.fields['equipe'].widget = forms.HiddenInput()
            self.form.fields['equipe'].required = False
        if not self.evento_record.edita_descricao:
            self.form.fields['descricao'].widget = forms.HiddenInput()
            self.form.fields['descricao'].required = False

    def form_initial(self):
        initial = super(EditaOrdem, self).form_initial()
        initial['classificacao'] = self.last_interacao.classificacao
        initial['equipe'] = self.last_interacao.equipe
        return initial

    def mount_context(self):
        try:
            msg = {}
            with transaction.atomic():
                self.doc = salva_interacao(
                    msg, self.request,
                    evento_cod=self.context['evento'],
                    doc_id=self.context['documento'],
                    classificacao=self.classificacao,
                    equipe=self.equipe,
                    descricao=self.descricao,
                )
        except Exception:
            self.context.update(msg)
            return
        doc_num = self.doc.id
        self.redirect = ('servico:ordem__get', doc_num)
