from pprint import pprint

from django.http import JsonResponse

from geral.functions import has_permission
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

    if not has_permission(request, 'lotes.libera_coleta_de_solicitacao'):
        data.update({
            'result': 'ERR',
            'descricao_erro': f'Usuário {request.user.username} sem '
                              'permissão para liberar coleta',
        })
        return JsonResponse(data, safe=False)

    try:
        sl.coleta = not sl.coleta
        sl.usuario = request.user
        sl.save()
    except Exception as e:
        data.update({
            'result': 'ERR',
            'descricao_erro': f'Erro ao alterar liberação de coleta: {e}',
        })
        return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
    })
    return JsonResponse(data, safe=False)
