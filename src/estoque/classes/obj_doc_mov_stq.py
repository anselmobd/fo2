from pprint import pprint

from django.db import connections

from estoque import models


class ObjDocMovStq():

    def __init__(self, num_doc, descricao, user):
        self.num_doc = num_doc
        self.descricao = descricao
        self.user = user

        self.cursor = connections['so'].cursor()

        self.valid_entries()

    def valid_entries(self):
        if self.num_doc == '0':
            if self.descricao.strip() == '':
                raise ValueError(
                    'Não é possível criar um número de documento sem uma '
                    'descrição.')
            self.num_doc = self.cria_num_doc()
        self.doc_mov_stq = models.DocMovStq.objects.filter(
            num_doc=self.num_doc, usuario=self.user)
        if len(self.doc_mov_stq) != 1:
            raise ValueError('Número de documento não encontrado.')

    def cria_num_doc(self):
        obj_docs = models.DocMovStq(
            descricao=self.descricao,
            usuario=self.user,
        )
        obj_docs.save()
        return obj_docs.get_num_doc
