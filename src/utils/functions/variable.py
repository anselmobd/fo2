from pprint import pprint


__all__ = ['is_empty']


def is_empty(value, also=None, only=None):
    """
    Testa se valor é vazio

    Por padrão retorna True se:
    - value for None;
    - for string vazia ou em branco;
    - for number com valor 0.

    Parametros:
    - also: enumerate com outros valores a serem considerados
      como vazios, além do padrão citado acima.
    - only: enumerate os únicos valores a serem considerados
      como vazios, sobrepondo o padrão citado acima.
    """

    def in_sequence(value, enum):
        if isinstance(enum, str):
            enum = [enum]
        # catch TypeError, se não quiser erro quando also
        # não é tuple ou list ou outro enumerate
        for item in enum:
            if value == item:
                return True
        return False

    if only:
        return in_sequence(value, only)

    try:
        value = value.strip()
    except AttributeError:
        pass
    result = not value

    if not result and also:
        return in_sequence(value, also)

    return result
