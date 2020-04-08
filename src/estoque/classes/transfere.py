from pprint import pprint

import systextil.models as sys_mod

from utils.functions import get_client_ip

import produto.functions as pro_fun
import produto.classes as pro_cla

from estoque import classes
from estoque import models
from estoque import queries


class Transfere():

    def __init__(
            self, cursor, request,
            tipo, nivel, ref, tam, cor, qtd,
            deposito_origem, deposito_destino,
            nova_ref, novo_tam, nova_cor,
            num_doc, descricao, cria_num_doc=True):
        self.can_exec = False

        self.cursor = cursor
        self.tipo = tipo
        self.nivel = nivel
        self.ref = ref
        self.tam = tam
        self.cor = cor
        self.qtd = qtd
        self.deposito_origem = deposito_origem
        self.deposito_destino = deposito_destino
        self.nova_ref = nova_ref
        self.novo_tam = novo_tam
        self.nova_cor = nova_cor
        self.num_doc = num_doc
        self.descricao = descricao
        self.request = request
        self.cria_num_doc = cria_num_doc

        self.valid_entries()

        self.calc_vars()
        self.can_exec = True

    def calc_vars(self):
        if self.tem_trans_saida:
            self.estoque_origem = self.get_estoque(self.deposito_origem)
            self.novo_estoque_origem = self.estoque_origem - self.qtd
        else:
            self.estoque_origem = 0
            self.novo_estoque_origem = 0

        if self.tem_trans_entrada:
            self.estoque_destino = self.get_estoque(self.deposito_destino)
            self.novo_estoque_destino = self.estoque_destino + self.qtd
        else:
            self.estoque_destino = 0
            self.novo_estoque_destino = 0

        produto = queries.get_preco_medio_niv_ref_cor_tam(
            self.cursor, self.nivel, self.ref, self.cor, self.tam)
        try:
            self.preco_medio = produto[0]['preco_medio']
        except Exception:
            raise ValueError(
                f'Não encontrado o preço médio do item {self.str_item}.')

    def valid_entries(self):
        self.valid_tipo()
        self.valid_configuracao()
        self.valid_item()
        self.valid_quant()
        self.valid_deps()

        if self.tip_mov.renomeia:
            self.valid_novo_item()
        else:
            self.nova_ref = self.ref
            self.novo_tam = self.tam
            self.nova_cor = self.cor
            self.produto_novo_item = None

        self.valid_num_doc()

    def valid_tipo(self):
        if isinstance(self.tipo, models.TipoMovStq):
            self.tip_mov = self.tipo
        else:
            try:
                self.tip_mov = models.TipoMovStq.objects.get(codigo=self.tipo)
            except models.TipoMovStq.DoesNotExist as e:
                raise ValueError(
                    f'Tipo de movimento de estoque "{self.tipo}" '
                    'não cadastrado.')

    def valid_item(self):
        objs_prod = pro_cla.ObjsProduto(
            self.nivel, self.ref, self.tam, self.cor)

        self.str_item = objs_prod.str_item
        self.produto_item = objs_prod.produto_item

    def valid_quant(self):
        if self.qtd <= 0:
            raise ValueError(
                'Quantidade deve ser maior que zero.')

    def valid_deps(self):
        if not self.tem_trans_saida:
            self.deposito_origem = 0

        if not self.tem_trans_entrada:
            self.deposito_destino = 0

        if not self.tip_mov.renomeia and \
                self.deposito_origem == self.deposito_destino:
            raise ValueError('Depósitos devem ser diferentes.')

    def valid_novo_item(self):
        if (len(self.nova_ref) + len(self.novo_tam) +
                len(self.nova_cor)) == 0:
            raise ValueError('Algum novo código deve ser indicado.')

        if len(self.nova_ref) == 0:
            self.nova_ref = self.ref
        if len(self.novo_tam) == 0:
            self.novo_tam = self.tam
        if len(self.nova_cor) == 0:
            self.nova_cor = self.cor

        if (self.nova_ref == self.ref and
                self.novo_tam == self.tam and
                self.nova_cor == self.cor):
            raise ValueError('Alguma alteração de código (referência, cor ou '
                             'tamanho) deve ser indicada.')

        objs_novo_prod = pro_cla.ObjsProduto(
            self.nivel, self.nova_ref, self.novo_tam, self.nova_cor)

        self.str_novo_item = objs_novo_prod.str_item
        self.produto_novo_item = objs_novo_prod.produto_item

    def valid_num_doc(self):
        obj_doc_mov_stq = classes.ObjDocMovStq(
            self.num_doc, self.descricao, self.request.user,
            cria=self.cria_num_doc)
        if obj_doc_mov_stq.num_doc != '0':
            self.num_doc = obj_doc_mov_stq.num_doc
            self.doc_mov_stq = obj_doc_mov_stq.doc_mov_stq

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
            tipo_trans = sys_mod.TipoTransacao.validos.get(
                codigo_transacao=codigo)
        except sys_mod.TipoTransacao.DoesNotExist as e:
            raise ValueError(
                f'Não encontrada transação de {descricao} '
                f'"{codigo}" do tipo de movimento de estoque "{self.tipo}".')

        if tipo_trans.entrada_saida not in ent_sai:
            raise ValueError(
                f'Transação de {descricao} "{codigo}" '
                f'do tipo de movimento de estoque "{self.tipo}" é do '
                'tipo da operação errado.')

        if tipo_trans.entrada_saida == 'T':
            return 'S'
        else:
            return tipo_trans.entrada_saida

    def valid_configuracao(self):
        self.trans_saida = self.tip_mov.trans_saida
        self.tem_trans_saida = self.trans_saida != 0

        self.trans_entrada = self.tip_mov.trans_entrada
        self.tem_trans_entrada = self.trans_entrada != 0

        if self.tem_trans_saida:
            self.trans_saida_e_s = self.valid_transacao(
                self.trans_saida, 'ST', 'saída')

        if self.tem_trans_entrada:
            self.trans_entrada_e_s = self.valid_transacao(
                self.trans_entrada, 'E', 'entrada')

    def exec(self):
        if not self.can_exec:
            raise ValueError(
                'Execução impedida por algum erro de inicialização.')

        if self.tem_trans_saida:
            self.insert(
                'saída',
                self.deposito_origem,
                self.trans_saida,
                self.trans_saida_e_s,
                )

        if self.tem_trans_entrada:
            self.insert(
                'entrada',
                self.deposito_destino,
                self.trans_entrada,
                self.trans_entrada_e_s,
                )

        mov_stq = models.MovStq(
            tipo_mov=self.tip_mov,
            item=self.produto_item,
            quantidade=self.qtd,
            deposito_origem=self.deposito_origem,
            deposito_destino=self.deposito_destino,
            novo_item=self.produto_novo_item,
            documento=self.doc_mov_stq,
            usuario=self.request.user,
        )
        mov_stq.save()

    def insert(self, descr, dep, trans, e_s):
        if descr == 'entrada':
            ref = self.nova_ref
            tam = self.novo_tam
            cor = self.nova_cor
        else:
            ref = self.ref
            tam = self.tam
            cor = self.cor

        if not queries.insert_transacao(
                self.cursor,
                dep,
                self.nivel,
                ref,
                tam,
                cor,
                self.num_doc,
                trans,
                e_s,
                self.qtd,
                self.preco_medio,
                self.request.user,
                get_client_ip(self.request)
                ):
            raise ValueError(
                f'Erro ao inserir transação de {descr}.')
