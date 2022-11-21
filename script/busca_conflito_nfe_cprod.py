import glob
from pprint import pprint
from xml.dom import minidom
import xml.etree.ElementTree as ET

# # parse an xml file by name
# file = minidom.parse('33220902485300000133550010000020911000961304_74e8628326d2e84daf901dc222c9967a6451e23f.xml')

# dets = file.getElementsByTagName('det')

# pprint(dets)

# for det in dets[:1]:
#     prod = det.getElementsByTagName('prod')
#     # cProd = prod.getElementsByTagName('cProd')
#     pprint(prod)
#     # help(prod)
#     # cProd = prod.getChieldByTagName('cProd')
#     # pprint(prod[0].firstChild.data)
#     pprint(prod[0].childNodes)
#     for node in prod[0].childNodes[:1]:
#         pprint(node)
#         # pprint(f"{node}")
#         print("node.tagName")
#         pprint(node.tagName)
#         # help(node)
#     # models[1].childNodes[0].data)
#     # for prod in prod:
#     #     print(elem.firstChild.data)

def parse_file(file_name, prods):

    tree = ET.parse(file_name)
    root = tree.getroot()

    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

    def get_in(level, node):
        return level.findall(f'nfe:{node}', ns)

    def get0_in(level, node):
        return get_in(level, node)[0]

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
    if cnpj in [
        '07681643000278',  # tussor
        '33966120000105',  # agator
    ]:
        return
    # pprint(CNPJ)
    # pprint(CNPJ.text)

    # pprint(infNFe)
    # dets = infNFe.findall('nfe:det', ns)
    dets = get_in(infNFe, 'det')
    # pprint(dets)

    for det in dets:
        prod = det.findall('nfe:prod', ns)[0]
        # pprint(prod)
        cProd = prod.findall('nfe:cProd', ns)[0]
        # pprint(cProd)
        # print(cProd.text)

        xProd = prod.findall('nfe:xProd', ns)[0]
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

        # prods[cProd.text].add(
        #     f"{xProd.text} | "
        #     # f"NF {cNF.text} | "
        #     # f"serie {serie.text} | "
        #     f"CNPJ {CNPJ.text}"
        # )
        
        prod_cnpj_x.add(c_nf)

files = glob.iglob('./*.xml')
# pprint(files)

prods = {}

# files = [
#     "33220902485300000133550010000020911000961304_74e8628326d2e84daf901dc222c9967a6451e23f.xml",
#     "33220904951454000107550010000089101082460214_2747be59341b99fcc31e78e244a1c77beeb67535.xml",
# ]
for file in files:
    parse_file(file, prods)

prods2 = {
    k: prods[k]
    for k in prods
    if len(prods[k]['x_prod']) > 1
    # and not k.startswith("1.M")
    # and not k.startswith("1.0")
    # and not k.startswith("1.C")
    # and not k.startswith("1.F")
    # and not k.endswith("33966120000105")
}

# pprint(prods2)
for k in prods2:
    print('código:', k)
    for cnpj in prods2[k]['cnpj']:
        print('  cnpj:', cnpj)
        prod_cnpj = prods2[k]['cnpj'][cnpj]
        for x_prod in prod_cnpj:
            print('    x_prod:', x_prod)
            print('      nf:', ', '.join(prod_cnpj[x_prod]))
