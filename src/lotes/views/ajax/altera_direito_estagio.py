from pprint import pprint

from django.http import JsonResponse

from fo2.connections import db_cursor_so

import lotes.queries as queries


def altera_direito_estagio(request, id):
    cursor = db_cursor_so(request)
    data = {
        'id': id,
    }
    erro = False
    ids = id.split('_')
    estagio = ids[0]
    usuario = ids[1]
    coluna = ids[2]

    data_r = queries.responsavel(
        cursor, 't', 'e', estagio, '', usuario)
    if len(data_r) == 0:
        row = {
            'CO': ' ',
            'AO': ' ',
            'BL': ' ',
            'EL': ' ',
        }
    else:
        row = data_r[0]

    state = row[coluna]
    acao = []

    if coluna == 'CO':
        if state == 'X':
            acao.append(['exclui', 3])
        else:
            acao.append(['inclui', 3])

    elif coluna == 'AO':
        if state == 'X':
            acao.append(['exclui', 4])
        else:
            acao.append(['inclui', 4])

    elif coluna == 'BL':
        if state == 'X':
            acao.append(['exclui', 1])
            acao.append(['exclui', 2])
            acao.append(['altera', 0, 2])
        else:
            if row['EL'] == 'X':
                acao.append(['altera', 2, 0])
            else:
                acao.append(['inclui', 1])

    elif coluna == 'EL':
        if state == 'X':
            acao.append(['exclui', 2])
            acao.append(['exclui', 1])
            acao.append(['altera', 0, 1])
        else:
            if row['BL'] == 'X':
                acao.append(['altera', 1, 0])
            else:
                acao.append(['inclui', 2])

    result = True
    for passo in acao:
        if result:
            tipo_acao = passo[0]
            if tipo_acao == 'inclui':
                tipo_movimento = passo[1]
                result = result and queries.responsavel_inclui_direitos(
                    cursor, estagio, usuario, tipo_movimento)

            elif tipo_acao == 'exclui':
                tipo_movimento = passo[1]
                result = result and queries.responsavel_exclui_direitos(
                    cursor, estagio, usuario, tipo_movimento)

            elif tipo_acao == 'altera':
                tipo_movimento_de = passo[1]
                tipo_movimento_para = passo[2]
                result = result and queries.responsavel_altera_direitos(
                    cursor, estagio, usuario,
                    tipo_movimento_de, tipo_movimento_para)
    erro = not result

    if erro:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao alterar direito',
        })
        return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
        'state': state,
    })
    return JsonResponse(data, safe=False)
