from pprint import pprint


def dados_to_grade(
    dados,
    field_linha=None,
    facade_linha=None,
    field_coluna=None,
    facade_coluna=None,
    field_ordem_coluna=None,
    field_quantidade=None,
):
    total = 'Total'

    if facade_linha is None:
        facade_linha = field_linha.capitalize()

    if facade_coluna is None:
        facade_coluna = field_coluna.capitalize()

    if not field_ordem_coluna:
        field_ordem_coluna = field_coluna

    indices_linhas = sorted(list(set([
        row[field_linha]
        for row in dados
    ])))

    indices_colunas_ordem = sorted(
        list(set([
            (row[field_coluna], row[field_ordem_coluna])
            for row in dados
        ])),
        key=lambda x: x[1],
    )
    indices_colunas = [
        r[0]
        for r in indices_colunas_ordem
    ]

    fields = [field_linha] + indices_colunas + [total]

    facades_list = []
    if facade_linha:
        facades_list.append(facade_linha)
    if facade_coluna:
        facades_list.append(facade_coluna)
    if not facades_list:
        facades_list['']    
    facedes = ' / '.join(facades_list)

    headers = [facedes] + indices_colunas + [total]

    style = {}
    for i in range(len(indices_colunas)):
        style[i+2] ='text-align: right;'
    style[len(indices_colunas)+2] = 'text-align: right;font-weight: bold;'

    data = []
    total_rows = {
        field_linha: total,
        '|STYLE': 'font-weight: bold;',
    }
    for coluna in indices_colunas:
        total_rows[coluna] = 0
    total_rows[total] = 0
    for linha in indices_linhas:
        row = {field_linha: linha}
        total_row = 0
        for coluna in indices_colunas:
            quantidades = [
                row[field_quantidade]
                for row in dados
                if (
                    row[field_linha] == linha
                    and row[field_coluna] == coluna
                )
            ]
            quantidade = sum(quantidades)
            row[coluna] = quantidade
            total_row += quantidade
            total_rows[coluna] += quantidade
            total_rows[total] += quantidade
        row[total] = total_row
        data.append(row)
    data.append(total_rows)

    return {
        'indices_linhas': indices_linhas,
        'indices_colunas': indices_colunas,
        'facedes': facedes,
        'fields': fields,
        'headers': headers,
        'style': style,
        'data': data,
        'total': total_rows[total],
    }
