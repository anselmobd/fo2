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

        self.produto_item = None
        self.produto_novo_item = None
        self.itens_extras = ''
        self.itens_extras_sep = ''
        self.str_item = ''

        self.valid_entries()
        self.calc_itens()

        self.calc_preco_medio()
        self.can_exec = True

    def calc_itens_lista(self, tem_trans, deposito, sinal, item_lista):
        for item in item_lista:
            if tem_trans:
                item['estoque_inicio'] = self.get_estoque(
                    deposito, self.nivel, item['ref'], item['cor'], item['tam'])
                item['estoque_fim'] = item['estoque_inicio'] + (self.qtd * sinal)
            else:
                item['estoque_inicio'] = 0
                item['estoque_fim'] = 0

    def calc_itens(self):
        self.calc_itens_lista(
            self.tem_trans_saida, self.deposito_origem, -1, self.itens_saida)
        self.calc_itens_lista(
            self.tem_trans_entrada, self.deposito_destino, +1, self.itens_entrada)
        
    def calc_preco_medio(self):
        try:
            item = self.itens_saida[0]
            produto = queries.get_preco_medio_niv_ref_cor_tam(
                self.cursor, self.nivel, item['ref'], item['cor'], item['tam'])
            self.preco_medio = produto[0]['preco_medio']
        except Exception:
            raise ValueError(
                f'Não encontrado o preço médio do item {self.str_item}.')

    def valid_item_destino(self):
        if self.tip_mov.renomeia:
            if (len(self.nova_ref) + len(self.novo_tam) +
                    len(self.nova_cor)) == 0:
                raise ValueError('Algum novo código deve ser indicado.')

        if len(self.nova_ref) == 0:
            self.nova_ref = self.ref
        if len(self.novo_tam) == 0:
            self.novo_tam = self.tam
        if len(self.nova_cor) == 0:
            self.nova_cor = self.cor

        if self.tip_mov.unidade != '1':
            if self.nova_cor == self.cor:
                raise ValueError('Em montagem e desmontagem as cores nunca são iguais.')

        self.novo_item_igual = (
            self.nova_ref == self.ref and
            self.novo_tam == self.tam and
            self.nova_cor == self.cor
        )

        if self.tip_mov.renomeia:
            if self.novo_item_igual:
                raise ValueError('Alguma alteração de código (referência, cor ou '
                                'tamanho) deve ser indicada.')

    def monta_itens_saida_entrada(self, item_lista, ref, cor, tam):
        cores = cor.split()
        for cor in cores:
            item_lista.append({
                'ref': ref,
                'cor': cor,
                'tam': tam,
            })

    def monta_itens_listas(self):
        self.itens_saida = []
        self.monta_itens_saida_entrada(self.itens_saida, self.ref, self.cor, self.tam)

        self.itens_entrada = []
        self.monta_itens_saida_entrada(
                self.itens_entrada, self.nova_ref, self.nova_cor, self.novo_tam)

    def valid_itens_lista(self, item_lista):
        produto_item = None
        for item in item_lista:
            objs_prod = pro_cla.ObjsProduto(
                self.nivel, item['ref'], item['tam'], item['cor'])
            item.update({
                'str_item': objs_prod.str_item,
                'produto_item': objs_prod.produto_item,
            })
            if produto_item is None:
                produto_item = objs_prod.produto_item
                self.str_item = objs_prod.str_item
            else:
                self.itens_extras += self.itens_extras_sep + objs_prod.str_item
                self.itens_extras_sep = ' '

        return produto_item

    def valid_itens(self):
        produto_item = self.valid_itens_lista(self.itens_saida)
        if self.produto_item is None:
            self.produto_item = produto_item

        produto_item = self.valid_itens_lista(self.itens_entrada)
        if self.produto_item is None:
            self.produto_item = produto_item
        else:
            self.produto_novo_item = produto_item


    def valid_entries(self):
        self.valid_tipo()
        self.valid_configuracao()
        self.valid_quant()
        self.valid_deps()
        self.valid_item_destino()
        self.monta_itens_listas()
        self.valid_itens()
        self.valid_num_doc()

    def valid_tipo(self):
        if isinstance(self.tipo, models.TipoMovStq):
            self.tip_mov = self.tipo
        else:
            try:
                self.tip_mov = models.TipoMovStq.objects.get(codigo=self.tipo)
            except models.TipoMovStq.DoesNotExist:
                raise ValueError(
                    f'Tipo de movimento de estoque "{self.tipo}" '
                    'não cadastrado.')

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

    def valid_num_doc(self):
        obj_doc_mov_stq = classes.ObjDocMovStq(
            self.num_doc, self.descricao, self.request.user,
            cria=self.cria_num_doc)
        if obj_doc_mov_stq.num_doc != '0':
            self.num_doc = obj_doc_mov_stq.num_doc
            self.doc_mov_stq = obj_doc_mov_stq.doc_mov_stq

    def get_estoque(self, deposito_field, nivel, ref, cor, tam):
        l_estoque = queries.get_estoque_dep_niv_ref_cor_tam(
            self.cursor, deposito_field, nivel, ref, cor, tam)
        if len(l_estoque) == 0:
            return 0
        else:
            return l_estoque[0]['estoque']

    def valid_transacao(self, codigo, ent_sai, descricao):
        try:
            tipo_trans = sys_mod.TipoTransacao.validos.get(
                codigo_transacao=codigo)
        except sys_mod.TipoTransacao.DoesNotExist:
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
            self.insert_lista(
                'saída',
                self.itens_saida,
                self.deposito_origem,
                self.trans_saida,
                self.trans_saida_e_s,
                )

        if self.tem_trans_entrada:
            self.insert_lista(
                'entrada',
                self.itens_entrada,
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
            itens_extras=self.itens_extras,
        )
        mov_stq.save()

    def insert_lista(self, descr, item_lista, dep, trans, e_s):
        for item in item_lista:
            self.insert(
                descr,
                item['ref'],
                item['tam'],
                item['cor'],
                dep,
                trans,
                e_s,
            )

    def insert(self, descr, ref, tam, cor, dep, trans, e_s):
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
