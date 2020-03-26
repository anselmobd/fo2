from pprint import pprint

from django.db import connections

import systextil.queries as sys_que

import produto.functions as pro_fun
import produto.models as pro_mod


class objs_produto():

    def __init__(self, nivel, ref, tam, cor):
        self.nivel = nivel
        self.ref = ref
        self.tam = tam
        self.cor = cor

        self.item = pro_fun.item_str(self.nivel, self.ref, self.tam, self.cor)
        self.cursor = connections['so'].cursor()

        self.valid_entries()

    def valid_entries(self):
        s_produtos = sys_que.item(
            self.cursor, self.nivel, self.ref, self.tam, self.cor)
        if len(s_produtos) == 0:
            raise ValueError(f'Item {self.item} não encontrado.')
        s_produto = s_produtos[0]

        try:
            self.produto = pro_mod.Produto.objects.get(referencia=self.ref)
        except pro_mod.Produto.DoesNotExist as e:
            self.produto = None

        if self.produto is None:
            self.produto = pro_mod.Produto(
                referencia=self.ref,
                descricao=s_produto['descr'],
            )
            self.produto.save()

    def get_produto(self):
        return self.produto
