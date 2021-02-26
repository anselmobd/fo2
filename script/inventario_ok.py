#!/usr/bin/env python

import locale
import numpy as np
import os.path
import pandas as pd
import sys
from pprint import pprint

locale.setlocale(locale.LC_ALL, '')

if len(sys.argv) < 2:
    print(sys.argv[0], '../9999_99')
    sys.exit()

def file_ok(name):
    if os.path.isfile(name):
        return True
    else:
        return False

ano_mes = sys.argv[1]
ods = ano_mes+'inventario_revisado.ods'
f0200 = ano_mes+'_0200.txt'
fk200 = ano_mes+'_k200.txt'

if not (file_ok(ods)):
    print('Planilha não acessível')
    sys.exit()

if not (file_ok(f0200)):
    print('0200 não acessível')
    sys.exit()

if not (file_ok(fk200)):
    print('k200 não acessível')
    sys.exit()

df_alt = pd.read_excel(ods, index_col=0)
# pprint(df_alt)

k200_file = pd.read_csv(
    fk200, sep='|', skiprows=2, header=None,
    names=['NaN1', 'k200', 'data', 'item', 'qtd', 'zero', 'NaN2', 'NaN3']
)
k200_file['qtd'] = k200_file['qtd'].apply(locale.atof)
# pprint(k200_file)

z200_file = pd.read_csv(
    f0200, sep='|', header=None, dtype=str,
)
# pprint(z200_file)

for item in df_alt.index:
    if item is not np.nan:
        qtd_alt = df_alt.loc[item, 'Quantidade']
        rec_k200 = k200_file[k200_file.item==item]
        if rec_k200.empty:
            print(f"{item} não encontrado no K200")
        else:
            rec_k200_idx = rec_k200.index.item()
            qtd_k200 = rec_k200.qtd.item()
            if qtd_alt != qtd_k200:
                if qtd_alt == 0:
                    print(f"{item} {qtd_k200} -> ZERAR!!!!")
                    k200_file = k200_file.drop(rec_k200_idx)
                    z200_file = z200_file.drop(rec_k200_idx)
                else:
                    print(f"{item} {qtd_k200} -> {qtd_alt}")
                    k200_file.at[rec_k200_idx, 'qtd'] = qtd_alt
    # break

fk200_tmp = ano_mes+'_k200_tmp.txt'
fk200_ok = ano_mes+'_k200_ok.txt'
f0200_ok = ano_mes+'_0200_ok.txt'

# pprint(k200_file)
k200_file.to_csv(
    fk200_tmp, sep='|', header=False, index=False,
    decimal=',', float_format='%.2f',
)
        
# pprint(z200_file)
z200_file.to_csv(
    f0200_ok, sep='|', header=False, index=False,
)
        
filenames = [(fk200, 2), (fk200_tmp, 0)]
with open(fk200_ok, 'w') as outfile:
    for afile in filenames:
        fname = afile[0]
        lines = afile[1]
        with open(fname) as infile:
            for num, line in enumerate(infile, 1):
                if lines:
                    if num > lines:
                        break
                outfile.write(line)
