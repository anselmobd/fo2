from pprint import pprint

from django.http import JsonResponse

from utils.functions.digits import fo2_digit_valid

from lotes.models import SolicitaLote


def libera_coleta_de_solicitacao(request, num):
    data = {
        'num': num,
    }

    if not fo2_digit_valid(num):
        data.update({
            'result': 'ERR',
            'descricao_erro': f'Número de solicitação #{num} inválido',
        })
        return JsonResponse(data, safe=False)

    id = num[:-2]

    try:
        sl = SolicitaLote.objects.get(id=id)
    except SolicitaLote.DoesNotExist:
        data.update({
            'result': 'ERR',
            'descricao_erro': f'Solicitação #{num} não encontrada',
        })
        return JsonResponse(data, safe=False)

    if not sl.concluida:
        data.update({
            'result': 'ERR',
            'descricao_erro': f'Solicitação #{num} não concluída',
        })
        return JsonResponse(data, safe=False)

    # sl.coleta = not sl.coleta

    # data.update({
    #     'result': 'ERR',
    #     'descricao_erro': 'Erro ao alterar liberação de coleta',
    # })
    # return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
        'state': 'state',
    })
    return JsonResponse(data, safe=False)
