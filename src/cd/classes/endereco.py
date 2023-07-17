from pprint import pprint

from cd.functions.endereco import endereco_split


class EnderecoCd():
    def __init__(self, endereco=None) -> None:
        # private
        self._endereco = None

        # init
        self.endereco = endereco

        # properties
        self.properties_padrao()

    def properties_padrao(self):
        self.valido = False
        self.espaco = 'Não endereçado'
        self.espaco_cod = 0
        self.bloco = '-'
        self.andar = '-'
        self.coluna = '-'
        self.prioridade = 7
        self.order_ap = 0

    @property
    def endereco(self):
        return self._endereco

    @endereco.setter
    def endereco(self, endereco):
        if self._endereco != endereco:
            self._endereco = endereco
            self._mount_details()

    def _mount_details(self):
        parts = endereco_split(self.endereco)
        if self.endereco:
            tamanho = len(self.endereco)
            self.valido = True
            self.bloco = parts['bloco']
            self.andar = parts['andar']
            self.coluna = parts['coluna']
            if tamanho != 6:
                self.valido = False
                self.prioridade = 5
                self.order_ap = 0
                self.espaco = 'Indefinido (len)'
                self.espaco_cod = None
            elif parts['espaco'] == '1' and parts['bloco'] in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                self.prioridade = 1
                self.order_ap = 10000 + int(parts['coluna']) * 100 + int(parts['andar'])
                self.espaco = 'Estantes'
                self.espaco_cod = 1
            elif parts['espaco'] == '1' and parts['bloco'] == 'L':
                self.prioridade = 2
                self.order_ap = int(parts['apartamento'])
                self.espaco = 'Lateral'
                self.espaco_cod = 1
            elif parts['espaco'] == '1' and parts['bloco'] == 'Q':
                self.prioridade = 3
                self.order_ap = int(parts['apartamento'])
                self.espaco = 'Agator'
                self.espaco_cod = 1
            elif parts['espaco'] == '2' and parts['bloco'] in ['S', 'X', 'Y', 'Z']:
                self.prioridade = 4
                self.order_ap = int(parts['apartamento'])
                self.espaco = 'Externo'
                self.espaco_cod = 2
            else:
                self.valido = False
                self.prioridade = 6
                self.order_ap = 0
                self.espaco = 'Indefinido (else)'
                self.espaco_cod = None
        else:
            self.properties_padrao()

    @property
    def details_dict(self):
        return {
            'valido': self.valido,
            'espaco': self.espaco,
            'espaco_cod': self.espaco_cod,
            'bloco': self.bloco,
            'andar': self.andar,
            'coluna': self.coluna,
            'prioridade': self.prioridade,
            'order_ap': self.order_ap,
        }
