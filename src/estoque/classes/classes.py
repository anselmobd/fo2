from pprint import pprint


class TransacoesDeAjuste():

    def __init__(self):
        self.transacoes = {
            1: {
                'codigo': 105,
                'es': 'E',
                'descr': 'Entrada por inventário',
            },
            -1: {
                'codigo': 3,
                'es': 'S',
                'descr': 'Saída por inventário',
            },
        }

    def get(self, sinal):
        trans = self.transacoes[sinal]['codigo']
        es = self.transacoes[sinal]['es']
        descr = self.transacoes[sinal]['descr']
        return trans, es, descr
