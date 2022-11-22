#!/usr/bin/env python3

import glob
import xml.etree.ElementTree as ET
from pprint import pprint


_NS = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
_CNPJ_IGN = [
    '07681643000278',  # tussor
    '33966120000105',  # agator
]


def get_in(level, node):
    return level.findall(f'nfe:{node}', _NS)


def get0_in(level, node):
    return get_in(level, node)[0]


def parse_nfe(file_name, prods):

    tree = ET.parse(file_name)
    root = tree.getroot()

    try:
        NFe = get0_in(root, 'NFe')
    except IndexError:
        return

    infNFe = get0_in(NFe, 'infNFe')

    ide = get0_in(infNFe, 'ide')
    cNF = get0_in(ide, 'cNF')

    emit = get0_in(infNFe, 'emit')
    CNPJ = get0_in(emit, 'CNPJ')
    cnpj = CNPJ.text
    if cnpj in _CNPJ_IGN:
        return

    dets = get_in(infNFe, 'det')

    for det in dets:
        prod = get0_in(det, 'prod')
        cProd = get0_in(prod, 'cProd')

        xProd = get0_in(prod, 'xProd')

        c_prod = cProd.text
        x_prod = xProd.text
        c_nf = cNF.text

        if c_prod not in prods:
            prods[c_prod] = {
                'x_prod': set(),
                'cnpj': {},
            }
        prods[c_prod]['x_prod'].add(x_prod)

        if cnpj not in prods[c_prod]['cnpj']:
            prods[c_prod]['cnpj'][cnpj] = {}
        prod_cnpj = prods[c_prod]['cnpj'][cnpj]

        if x_prod not in prod_cnpj:
            prod_cnpj[x_prod] = set()       

        prod_cnpj_x = prod_cnpj[x_prod]

        prod_cnpj_x.add(c_nf)


if __name__ == '__main__':

    files = glob.iglob('./*.xml')

    produtos = {}

    for file in files:
        parse_nfe(file, produtos)

    prods = {
        k: produtos[k]
        for k in produtos
        if len(produtos[k]['x_prod']) > 1
    }

    for k in prods:
        print(f"cprod: '{k}'")
        for cnpj in prods[k]['cnpj']:
            print(f"  cnpj: {cnpj}")
            prod_cnpj = prods[k]['cnpj'][cnpj]
            for x_prod in prod_cnpj:
                print(f"    xprod: '{x_prod}'")
                print("      nf:", ", ".join(prod_cnpj[x_prod]))
