from pprint import pprint

__all__ = ['nf_situacao_descr']
__version__ = '0.1 220131.1443'
__author__ = 'Oxigenai'


_SITUACAO_DESCR = {
    0: "Calculada",
    9: {
        101: "Ativa",  # emitida
        None: "Rejeitada",
    },
    2: "Cancelada",
    3: "Verificar",
    4: "Confirmada",
    5: "Incompleta",
    6: "Incompleta",  # porém foi calculada a duplicata
    None: "Desconhecida"
}


def nf_situacao_descr(situacao, status):

    descr = _SITUACAO_DESCR.get(situacao, "DESCONHECIDO")
    if isinstance(descr, dict):
        try:
            descr = descr[status]
        except KeyError:
            descr = descr[None]
    return descr
