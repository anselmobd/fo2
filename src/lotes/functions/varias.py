from pprint import pprint


def periodo_oc(lote):
    if len(lote) == 9:
        return lote[:4], lote[4:]
