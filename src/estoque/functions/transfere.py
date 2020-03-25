from pprint import pprint

from estoque import queries


class Transfere():

    def __init__(
            self, cursor, nivel, ref, tam, cor, qtd,
            deposito_origem, deposito_destino):
        self.cursor = cursor
        self.nivel = nivel
        self.ref = ref
        self.tam = tam
        self.cor = cor
        self.qtd = qtd
        self.deposito_origem = deposito_origem
        self.deposito_destino = deposito_destino

        self.initial_vars()
        self.valid_entries()
        self.calc_vars()

    def initial_vars(self):
        self.item = f'{self.nivel}.{self.ref}.{self.tam}.{self.cor}'

    def calc_vars(self):
        self.estoque_origem = self.get_estoque(self.deposito_origem)
        self.estoque_destino = self.get_estoque(self.deposito_destino)
        self.novo_estoque_origem = self.estoque_origem - self.qtd
        self.novo_estoque_destino = self.estoque_destino + self.qtd

    def valid_entries(self):
        self.valid_item()
        self.valid_deps()

    def valid_item(self):
        produto = queries.get_preco_medio_niv_ref_cor_tam(
            self.cursor, self.nivel, self.ref, self.cor, self.tam)
        if len(produto) == 0:
            raise ValueError(f'Item {self.item} não encontrado.')

    def valid_deps(self):
        if self.deposito_origem == self.deposito_destino:
            raise ValueError('Depósitos devem ser diferentes')

    def get_estoque(self, deposito_field):
        l_estoque = queries.get_estoque_dep_niv_ref_cor_tam(
            self.cursor, deposito_field,
            self.nivel, self.ref, self.cor, self.tam)
        if len(l_estoque) == 0:
            return 0
        else:
            return l_estoque[0]['estoque']

    def exec(self):
        raise ValueError('SQL erro')
        pass
