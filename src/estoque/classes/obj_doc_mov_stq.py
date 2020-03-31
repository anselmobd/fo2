from pprint import pprint

from django.db import connections

from base.models import Colaborador
from systextil.models import Usuario as S_Usuario

from estoque import models


class ObjDocMovStq():

    def __init__(self, num_doc, descricao, user):
        self.num_doc = num_doc
        self.descricao = descricao
        self.user = user

        self.cursor = connections['so'].cursor()

        self.get_num_doc()

        self.valid_user()

    def get_num_doc(self):
        if self.num_doc == '0':
            self.cria_num_doc()
        else:
            self.valid_num_doc()
            self.valid_user()

    def valid_num_doc(self):
        self.doc_mov_stq = models.DocMovStq.objects.filter(
            num_doc=self.num_doc, usuario=self.user)
        if len(self.doc_mov_stq) != 1:
            raise ValueError('Número de documento não encontrado.')

    def cria_num_doc(self):
        self.valid_descricao()
        self.valid_user()

        self.doc_mov_stq = models.DocMovStq(
            descricao=self.descricao,
            usuario=self.user,
        )
        self.doc_mov_stq.save()
        self.num_doc = self.doc_mov_stq.get_num_doc

    def valid_descricao(self):
        if self.descricao.strip() == '':
            raise ValueError(
                'Não é possível criar um número de documento sem uma '
                'descrição.')

    def valid_user(self):
        try:
            colab = Colaborador.objects.get(user=self.user)
        except Colaborador.DoesNotExist as e:
            raise ValueError(
                'Não é possível utilizar um usuário que não está cadastrado '
                'como colaborador.')

        try:
            s_user = S_Usuario.objects.get(codigo_usuario=colab.matricula)
        except S_Usuario.DoesNotExist as e:
            raise ValueError(
                'Não é possível utilizar um colaborador sem matrícula válida '
                'ou inativo.')
