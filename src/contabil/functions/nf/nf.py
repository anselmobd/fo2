from pprint import pprint

from utils.functions.dict import dict_get_none


__all__ = ['nf_situacao_descr']
__version__ = '0.1 220131.1443'
__author__ = 'Oxigenai'


SITUACAO_DESCR = {
    0: "Calculada",
    1: {
        100: "Ativa",  # emitida
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
    descr = dict_get_none(SITUACAO_DESCR, situacao)
    if isinstance(descr, dict):
        descr = dict_get_none(descr, status)
    return descr
