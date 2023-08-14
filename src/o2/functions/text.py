from pprint import pprint

__all__=['split_size_by_char', 'splited']


def split_size_by_char(text, size_wanted, separator=' ', limit=None):
    """Split text in two
    Rules:
    - se o tamanho certo aceita uma quebra, aí será a quebra
    - senão, será no primeiro caractere diferente de separator 
      antes do primeiro grupo encontrado à esquerda do tamanho
      indicado
    - todos os caracteres iguais ao separador serão excluidos 
      do início da segunda parte do split
    """
    text = text.rstrip(separator)
    before = text
    after = ''
    if len(text) > size_wanted:
        size = size_wanted
        while size > 0 and text[size] != separator and (size > limit if limit else True):
            size -= 1
        while size > 1 and text[size-1] == separator:
            size -= 1
        if size == 0:
            if limit:
                size = limit
            else:
                size = size_wanted
        before = text[:size]
        while size < len(text) and text[size] == separator:
            size += 1
        if len(text) > size:
            after = text[size:]
    if before == separator:
        # Acontece se só tem separator antes do size ou do limit
        before = ''
    return before, after


def splited(text, separator=' '):
    """ Split text on separator by considering consequent separators as one
    """
    return list(filter(lambda x: x, text.split(separator)))
