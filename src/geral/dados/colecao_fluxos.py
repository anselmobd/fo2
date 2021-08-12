from pprint import pprint


def dict_colecao_fluxos(colecao, tipo, ref):
    cf = {
        (1, 2, 3, 4, 13, 15, ): {
            ('pa', 'pg', 'pb', ): {'': [1, 2, 3, 51]},
            ('md', ): {'M': [1, 51],
                       'C': [2],
                       'R': [3],
                       },
        },
        (5, ): {
            ('md', ): {'M': [51],
                       'C': [6],
                       },
        },
        (6, ): {
            ('md', ): {'M': [51]}
        },
        (7, ): {
            ('pa', 'pg'): {'': [7, 51]},
        },
        (8, ): {
            ('pa', ): {'': [5, '51p']},
            ('pg', ): {'': [5]},
            ('md', ): {'M': ['51p'],
                       'C': [5],
                       'F': [8],
                       },
        },
        (9, 10, 11, 12, 16, 17, ): {
            ('pa', 'pg', 'pb', 'md', ): {'': [4]},
        },
        (18, ): {
            ('pa', ): {'': ['1p', '2p', 5, '51p']},
            ('pg', ): {'': ['1p', 5]},
            ('md', ): {'M': ['1p', '51p'],
                       'C': ['2p', 5],
                       },
        },
        (50, ): {
            ('md', ): {'V': [8]}
        },
    }

    col_id = None
    for col_tuple in cf:
        if colecao in col_tuple:
            col_id = col_tuple
            break
    if col_id is None:
        return []
    col_dict = cf[col_id]

    tipo_id = None
    for tipo_tuple in col_dict:
        if tipo in tipo_tuple:
            tipo_id = tipo_tuple
            break
    if tipo_id is None:
        return []
    tipo_dict = col_dict[tipo_id]

    inicio = ['']
    if tipo == 'md':
        inicio.insert(0, ref[0])

    for ini in inicio:
        if ini in tipo_dict:
            return tipo_dict[ini]

    return []
