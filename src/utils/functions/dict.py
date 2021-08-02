def equal_dicts(d1, d2):
    ''' Devolve True se dicionários são iguais.
    Só funciona se todos os valores forem serializáveis.
    '''
    return len(d1.items() ^ d2.items()) == 0
