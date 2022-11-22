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

    # pprint(root)
    try:
        # NFe = root.findall('nfe:NFe', ns)[0]
        NFe = get0_in(root, 'NFe')
    except IndexError:
        return

    # pprint(NFe)
    # infNFe = NFe.findall('nfe:infNFe', ns)[0]
    infNFe = get0_in(NFe, 'infNFe')

    # ide = infNFe.findall('nfe:ide', ns)[0]
    ide = get0_in(infNFe, 'ide')
    # pprint(ide)
    # cNF = ide.findall('nfe:cNF', ns)[0]
    cNF = get0_in(ide, 'cNF')
    # pprint(cNF)
    # pprint(cNF.text)
    # serie = ide.findall('nfe:serie', ns)[0]
    serie = get0_in(ide, 'serie')
    # pprint(serie)
    # pprint(serie.text)

    # emit = infNFe.findall('nfe:emit', ns)[0]
    emit = get0_in(infNFe, 'emit')
    # pprint(emit)
    # CNPJ = emit.findall('nfe:CNPJ', ns)[0]
    CNPJ = get0_in(emit, 'CNPJ')
    cnpj = CNPJ.text
    if cnpj in _CNPJ_IGN:
        return
    # pprint(CNPJ)
    # pprint(CNPJ.text)

    # pprint(infNFe)
    # dets = infNFe.findall('nfe:det', ns)
    dets = get_in(infNFe, 'det')
    # pprint(dets)

    for det in dets:
        # prod = det.findall('nfe:prod', ns)[0]
        prod = get0_in(det, 'prod')
        # pprint(prod)
        # cProd = prod.findall('nfe:cProd', ns)[0]
        cProd = get0_in(prod, 'cProd')
        # pprint(cProd)
        # print(cProd.text)

        # xProd = prod.findall('nfe:xProd', ns)[0]
        xProd = get0_in(prod, 'xProd')
        # pprint(cProd)
        # print(xProd.text)

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

    # files = [
    #     "33220902485300000133550010000020911000961304_74e8628326d2e84daf901dc222c9967a6451e23f.xml",
    #     "33220904951454000107550010000089101082460214_2747be59341b99fcc31e78e244a1c77beeb67535.xml",
    # ]

    files = glob.iglob('./*.xml')
    # pprint(files)

    produtos = {}

    for file in files:
        parse_nfe(file, produtos)

    prods = {
        k: produtos[k]
        for k in produtos
        if len(produtos[k]['x_prod']) > 1
        # and not k.startswith("1.M")
        # and not k.startswith("1.0")
        # and not k.startswith("1.C")
        # and not k.startswith("1.F")
        # and not k.endswith("33966120000105")
    }

    # pprint(prods2)
    for k in prods:
        print(f"código: '{k}'")
        for cnpj in prods[k]['cnpj']:
            print(f"  cnpj: {cnpj}")
            prod_cnpj = prods[k]['cnpj'][cnpj]
            for x_prod in prod_cnpj:
                print(f"    x_prod: '{x_prod}'")
                print("      nf:", ", ".join(prod_cnpj[x_prod]))
