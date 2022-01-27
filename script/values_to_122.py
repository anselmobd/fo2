import csv
import sys
from pprint import pprint


with open(sys.argv[1]) as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=';')

    for row in csv_reader:
        ref = row['Referência']
        qtd = row['Quantidade na caixinha']
        tamanhos = row['Tamanhos'].split('-')
        cores = row['Cores'].split('-')
        for tamanho in tamanhos:
            for cor in cores:
                print(
                    "union all select 0, 0, '1', "
                    f"'{ref}', '{tamanho}', '0000{cor}', 122, {qtd} from dual"
                )
