class Produto():

    def __init__(self, nivel=None, ref=None, tam=None, cor=None):
        self.nivel = nivel
        self.ref = ref
        self.tam = tam
        self.cor = cor
        self.item = f'{nivel}.{ref}.{tam}.{cor}'
