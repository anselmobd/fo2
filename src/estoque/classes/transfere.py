from pprint import pprint

from django.db import connections

import systextil.models as sys_mod
import systextil.queries as sys_que

import produto.functions as pro_fun
import produto.models as pro_mod

from estoque import queries
from estoque import models


class objs_produto():

    def __init__(self, nivel, ref, tam, cor):
        self.nivel = nivel
        self.ref = ref
        self.tam = tam
        self.cor = cor

        self.cursor = connections['so'].cursor()

    def produto(self):
        s_produtos = sys_que.item(
            self.cursor, self.nivel, self.ref, self.tam, self.cor)
        if len(s_produtos) == 0:
            item = pro_fun.item_str(self.nivel, self.ref, self.tam, self.cor)
            raise ValueError(f'Item {item} não encontrado.')
        s_produto = s_produtos[0]

        try:
            produto = pro_mod.Produto.objects.get(referencia=self.ref)
        except pro_mod.Produto.DoesNotExist as e:
            produto = None

        if produto is None:
            produto = pro_mod.Produto(
                referencia=self.ref,
                descricao=s_produto['descr'],
            )
            produto.save()

        return produto


class Transfere():

    def __init__(
            self, cursor, nivel, ref, tam, cor, qtd,
            deposito_origem, deposito_destino):
        self.can_exec = False

        self.cursor = cursor
        self.nivel = nivel
        self.ref = ref
        self.tam = tam
        self.cor = cor
        self.qtd = qtd
        self.deposito_origem = deposito_origem
        self.deposito_destino = deposito_destino

        self.item = pro_fun.item_str(self.nivel, self.ref, self.tam, self.cor)

        self.valid_entries()
        self.valid_configuracao()

        self.calc_vars()
        self.can_exec = True

    def calc_vars(self):
        self.estoque_origem = self.get_estoque(self.deposito_origem)
        self.estoque_destino = self.get_estoque(self.deposito_destino)
        self.novo_estoque_origem = self.estoque_origem - self.qtd
        self.novo_estoque_destino = self.estoque_destino + self.qtd

        produto = queries.get_preco_medio_niv_ref_cor_tam(
            self.cursor, self.nivel, self.ref, self.cor, self.tam)
        try:
            self.preco_medio = produto[0]['preco_medio']
        except Exception:
            raise ValueError(
                f'Não encontrado o preço médio do item {self.item}.')

    def valid_entries(self):
        self.valid_item()
        self.valid_deps()

    def valid_item(self):
        objs_prod = objs_produto(self.nivel, self.ref, self.tam, self.cor)

        self.produto = objs_prod.produto()

    def valid_deps(self):
        if self.deposito_origem == self.deposito_destino:
            raise ValueError('Depósitos devem ser diferentes.')

    def get_estoque(self, deposito_field):
        l_estoque = queries.get_estoque_dep_niv_ref_cor_tam(
            self.cursor, deposito_field,
            self.nivel, self.ref, self.cor, self.tam)
        if len(l_estoque) == 0:
            return 0
        else:
            return l_estoque[0]['estoque']

    def valid_transacao(self, codigo, ent_sai, descricao):
        try:
            tipo_trans = sys_mod.TipoTransacao.objects.get(
                codigo_transacao=codigo)
        except sys_mod.TipoTransacao.DoesNotExist as e:
            raise ValueError(
                f'Não encontrada transação de {descricao} '
                f'"{codigo}" do tipo de movimento de estoque "TRANSF".')

        if tipo_trans.entrada_saida not in ent_sai:
            raise ValueError(
                f'Transação de {descricao} "{codigo}" '
                'do tipo de movimento de estoque "TRANSF" é do '
                'tipo da operação errado.')

        return tipo_trans.entrada_saida

    def valid_configuracao(self):
        try:
            tip_mov = models.TipoMovStq.objects.get(codigo='TRANSF')
        except models.TipoMovStq.DoesNotExist as e:
            raise ValueError(
                'Tipo de movimento de estoque "TRANSF" não cadastrado.')

        self.trans_saida = tip_mov.trans_saida
        self.trans_entrada = tip_mov.trans_entrada

        self.trans_saida_e_s = self.valid_transacao(
            self.trans_saida, 'ST', 'saída')
        self.trans_entrada_e_s = self.valid_transacao(
            self.trans_entrada, 'E', 'entrada')

    def exec(self):
        if not self.can_exec:
            raise ValueError(
                'Execução impedida por algum erro de inicialização.')

        return
        if not queries.insert_transacao_ajuste(
                self.cursor,
                self.deposito_origem,
                self.nivel,
                self.ref,
                self.tam,
                self.cor,
                '1',  # self.num_doc,
                self.trans_saida,
                self.trans_saida_e_s,
                self.qtd,
                self.preco_medio
                ):
            raise ValueError(
                'Erro ao inserir transação de saída.')
