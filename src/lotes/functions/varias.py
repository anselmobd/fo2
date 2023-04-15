from functools import lru_cache
from pprint import pprint

from utils.functions.strings import only_digits


def periodo_oc(lote):
    if len(lote) == 9:
        return lote[:4], lote[4:]


def lote_de_periodo_oc(periodo, oc):
    return f"{periodo}{oc:05}"


@lru_cache(maxsize=128)
def modelo_de_ref(ref):
    try:
        return int(only_digits(ref))
    except ValueError:
        return 0
