from pprint import pprint

__all__ = ['nf_situacao_descr']
__version__ = '0.1 220131.1443'
__author__ = 'Oxigenai'


_SITUACAO_DESCR = {
    0: "CALCULADA",
    1: {
        100: "ATIVA",  # EMITIDA
        None: "REJEITADA",
    },
    2: "CANCELADA",
    3: "VERIFICAR",
    4: "CONFIRMADA",
    5: "INCOMPLETA",
    6: "INCOMPLETA",  # porém foi calculada a duplicata
}


def nf_situacao_descr(situacao, status):

    descr = _SITUACAO_DESCR.get(situacao, "DESCONHECIDO")
    if isinstance(descr, dict):
        try:
            descr = descr[status]
        except KeyError:
            descr = descr[None]
    return descr
