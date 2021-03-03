from pprint import pprint 

from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse

from fo2.connections import db_cursor_so

from utils.views import request_hash_trail

import estoque.classes
from estoque import queries


@permission_required('base.can_adjust_stock')
def executa_ajuste(request, **kwargs):
    data = {}

    dep = kwargs['dep']
    ref = kwargs['ref']
    cor = kwargs['cor']
    tam = kwargs['tam']
    ajuste = kwargs['ajuste']
    num_doc = kwargs['num_doc']
    trail = kwargs['trail']

    if dep not in ['101', '102', '231']:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Depósito inválido',
        })
        return JsonResponse(data, safe=False)

    try:
        ajuste = int(ajuste)
        _ = 1 / ajuste  # erro, se zero
    except Exception:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Quantidade inválida para transação',
        })
        return JsonResponse(data, safe=False)

    cursor = db_cursor_so(request)

    produto = queries.get_preco_medio_ref_cor_tam(
        cursor, ref, cor, tam)
    try:
        preco_medio = produto[0]['preco_medio']
    except Exception:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Referência/Cor/Tamanho não encontrada',
        })
        return JsonResponse(data, safe=False)

    sinal = 1 if ajuste > 0 else -1
    transacoes = estoque.classes.TransacoesDeAjuste()
    trans, es, descr = transacoes.get(sinal)

    trail_check = request_hash_trail(
        request,
        dep,
        ref,
        cor,
        tam,
        ajuste,
    )
    if trail != trail_check:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Trail hash inválido',
            # 'trail_check': trail_check,
        })
        return JsonResponse(data, safe=False)

    quant = ajuste * sinal
    if queries.insert_transacao_ajuste(
            cursor,
            dep,
            ref,
            tam,
            cor,
            num_doc,
            trans,
            es,
            quant,
            preco_medio
            ):
        data.update({
            'result': 'OK',
            'descricao_erro': "Foi executada a transação '{:03}' ({}) "
                              "com a quantidade {}.".format(
                                trans,
                                es,
                                quant,
                              ),
        })
    else:
        data.update({
            'result': 'ERR',
            'descricao_erro': "Erro ao executar a transação '{:03}' ({}) "
                              "com a quantidade {}.".format(
                                trans,
                                es,
                                quant,
                              ),
        })

    return JsonResponse(data, safe=False)
