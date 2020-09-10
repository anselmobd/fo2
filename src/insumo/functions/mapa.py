from pprint import pprint


def calc_estoque_final_semana(row, com_receber=True):
    estoque = row['ESTOQUE'] \
        - row['NECESSIDADE'] \
        - row['NECESSIDADE_PASSADA'] \
        + row['RECEBIMENTO'] \
        + row['RECEBIMENTO_ATRASADO'] \
        + row['RECEBIMENTO_MOVIDO']
    if com_receber:
        estoque += row['RECEBER']
    return estoque


def recalc_estoque(data, qtd_estoque):
    estoque = qtd_estoque
    for row in data:
        row['ESTOQUE'] = estoque
        estoque = calc_estoque_final_semana(row)


def print_data(data):
    print(
        'Semana    ',
        'Estoque Real',
        'Necessidade',
        'Necessidade passada',
        'Recebimento',
        'Recebimento atrasado',
        'Recebimento movido',
        'Compra sugerida',
        'Compra atrasada',
        'Recebimento sugerido',
    )
    for row in data:
        print(
            f"{row['DATA']}",
            f"{row['ESTOQUE']:12.2f}",
            f"{row['NECESSIDADE']:11.2f}",
            f"{row['NECESSIDADE_PASSADA']:19.2f}",
            f"{row['RECEBIMENTO']:11.2f}",
            f"{row['RECEBIMENTO_ATRASADO']:20.2f}",
            f"{row['RECEBIMENTO_MOVIDO']:18.2f}",
            f"{row['COMPRAR']:15.2f}",
            f"{row['COMPRAR_PASSADO']:15.2f}",
            f"{row['RECEBER']:20.2f}",
        )
