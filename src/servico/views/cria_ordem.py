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
        self.Form_class = servico.forms.CriaInteracaoForm
        self.template_name = 'servico/cria_ordem.html'
        self.title_name = 'Cria ordem'


    def salva_evento(self):
        try:
            try:
                tipo = servico.models.TipoDocumento.objects.get(slug='os')
            except servico.models.TipoDocumento.DoesNotExist as e:
                self.context.update({
                    'erro': 'Tipo de documento inválido.',
                })
                raise e

            try:
                evento = servico.models.Evento.objects.get(
                    statusevento__status_pre=None)
            except servico.models.Evento.DoesNotExist as e:
                self.context.update({
                    'erro': 'Evento de criação não encontrado.',
                })
                raise e

            try:
                self.doc = servico.models.Documento(tipo=tipo)
                self.doc.save()
            except Exception as e:
                self.context.update({
                    'erro': 'Não foi possível gerar um número de documento.',
                })
                raise e

            try:
                evento = servico.models.Interacao(
                    documento=self.doc,
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
        except Exception as e:
            raise e

        else:
            # se não houve exceptions, tem que tentar salvar o csrf
            if csrf_used(self.request):
                self.context.update({
                    'erro': 'Formulário já gravado.',
                })
                raise Error


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


def salva_interacao(
        msg, request, tipo_documento="os", evento_cod=None,
        doc_id=None, nivel=None, equipe=None, descricao=None):
    """Salva uma interação de serviço
    Recebe:
        msg: deve ser iniciado com {} e recebe mensagens de erro
        request: importante para controle por csrf
        tipo_documento: Por ora apenas "os", ordem de serviço
        evento_cod: passa None quando for evento de criação ou codigo de um evento
        doc_id: None para criar um novo (evento de criação) ou id de um documento
        nivel
        equipe
        descrição
    Retorna:
        o documento que recebeu interação (criado ou não)
    """
    try:
        try:
            tipo = servico.models.TipoDocumento.objects.get(slug=tipo_documento)
        except servico.models.TipoDocumento.DoesNotExist as e:
            msg.update({
                'erro': 'Tipo de documento inválido.',
            })
            raise e

        if evento_cod is None:
            try:
                evento = servico.models.Evento.objects.get(
                    statusevento__status_pre=None)
            except servico.models.Evento.DoesNotExist as e:
                msg.update({
                    'erro': 'Evento de criação não encontrado.',
                })
                raise e
        else:
            try:
                evento = servico.models.Evento.objects.get(
                    codigo=evento_cod)
            except servico.models.Evento.DoesNotExist as e:
                msg.update({
                    'erro': f'Evento "{evento_cod}" não encontrado.',
                })
                raise e

        if doc_id is None:
            try:
                doc = servico.models.Documento(tipo=tipo)
                doc.save()
            except Exception as e:
                msg.update({
                    'erro': 'Não foi possível gerar um número de documento.',
                })
                raise e
        else:
            try:
                doc = servico.models.Documento.objects.get(id=doc_id)
                doc.save()
            except Exception as e:
                msg.update({
                    'erro': f'Não foi possível encontrar o documento "{doc_id}".',
                })
                raise e

        try:
            evento = servico.models.Interacao(
                documento=doc,
                evento=evento,
                nivel=nivel,
                equipe=equipe,
                descricao=descricao,
            )
            evento.save()
        except Exception as e:
            msg.update({
                'erro': 'Não foi possível gerar o evento de requisição.',
            })
            raise e

        doc.ativo = True
        doc.save()
    except Exception as e:
        raise e

    else:
        # se não houve exceptions, tem que tentar salvar o csrf
        if csrf_used(request):
            msg.update({
                'erro': 'Formulário já gravado.',
            })
            raise Error

    return doc
