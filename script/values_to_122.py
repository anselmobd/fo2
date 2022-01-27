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
                if sys.argv[2] == 'ita':
                    print(
                        f"ita(cursor, '122', '{ref}', '{tamanho}', '0000{cor}', 702114049, 105, 'E', {qtd}, 2, usuario, '192.168.1.242')"
                    )
                else:
                    print(
                        "union all select 0, 0, '1', "
                        f"'{ref}', '{tamanho}', '0000{cor}', 122, {qtd} from dual"
                    )
