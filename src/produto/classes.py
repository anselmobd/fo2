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

        self.set_vars()

    def set_vars(self):
        self.set_produto()
        self.set_produto_cor()
        self.set_tamanho()
        self.set_produto_tam()
        self.set_produto_item()

    def valid_entries(self):
        s_produtos = sys_que.item(
            self.cursor, self.nivel, self.ref, self.tam, self.cor)
        if len(s_produtos) == 0:
            raise ValueError(f'Item {self.item} não encontrado.')
        self.s_produto = s_produtos[0]

    def set_produto(self):
        try:
            self.produto = pro_mod.Produto.objects.get(
                nivel=self.nivel,
                referencia=self.ref,
            )
        except pro_mod.Produto.DoesNotExist as e:
            self.produto = None

        if self.produto is None:
            self.produto = pro_mod.Produto(
                nivel=self.nivel,
                referencia=self.ref,
                descricao=self.s_produto['descr'],
            )
            self.produto.save()

    def set_produto_cor(self):
        try:
            self.produto_cor = pro_mod.ProdutoCor.objects.get(
                produto=self.produto, cor=self.cor)
        except pro_mod.ProdutoCor.DoesNotExist as e:
            self.produto_cor = None

        if self.produto_cor is None:
            self.produto_cor = pro_mod.ProdutoCor(
                produto=self.produto,
                cor=self.cor,
                descricao=self.s_produto['descr_cor'],
            )
            self.produto_cor.save()

    def set_tamanho(self):
        try:
            self.tamanho = pro_mod.Tamanho.objects.get(
                nome=self.tam)
        except pro_mod.Tamanho.DoesNotExist as e:
            self.tamanho = None

        if self.tamanho is None:
            self.tamanho = pro_mod.Tamanho(
                nome=self.tam,
                ordem=self.s_produto['ordem_tam'],
            )
            self.tamanho.save()

    def set_produto_tam(self):
        try:
            self.produto_tam = pro_mod.ProdutoTamanho.objects.get(
                produto=self.produto, tamanho=self.tamanho)
        except pro_mod.ProdutoTamanho.DoesNotExist as e:
            self.produto_tam = None

        if self.produto_tam is None:
            self.produto_tam = pro_mod.ProdutoTamanho(
                produto=self.produto,
                tamanho=self.tamanho,
                descricao=self.s_produto['descr_tam'],
            )
            self.produto_tam.save()

    def set_produto_item(self):
        try:
            self.produto_item = pro_mod.ProdutoItem.objects.get(
                produto=self.produto,
                cor=self.produto_cor,
                tamanho=self.produto_tam,
            )
        except pro_mod.ProdutoItem.DoesNotExist as e:
            self.produto_item = None

        if self.produto_item is None:
            self.produto_item = pro_mod.ProdutoItem(
                produto=self.produto,
                cor=self.produto_cor,
                tamanho=self.produto_tam,
            )
            self.produto_item.save()
