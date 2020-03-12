from pprint import pprint

from django.http import JsonResponse

import lotes.models


def solicita_lote(request, solicitacao_id, lote, qtd):
    data = {}

    try:
        solicitacao = lotes.models.SolicitaLote.objects.get(
            id=solicitacao_id)
    except lotes.models.SolicitaLote.DoesNotExist:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Solicitação não encontrada por id',
        })
        return JsonResponse(data, safe=False)

    try:
        lote_rec = lotes.models.Lote.objects.get(lote=lote)
    except lotes.models.Lote.DoesNotExist:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Lote não encontrado',
        })
        return JsonResponse(data, safe=False)

    try:
        iqtd = int(qtd)
    except ValueError:
        iqtd = -1
    if iqtd < 1 or iqtd > lote_rec.qtd:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Quantidade inválida',
        })
        return JsonResponse(data, safe=False)

    try:
        solicita = lotes.models.SolicitaLoteQtd()
        solicita.solicitacao = solicitacao
        solicita.lote = lote_rec
        solicita.qtd = iqtd
        solicita.save()
    except lotes.models.Lote.DoesNotExist:
        data.update({
            'result': 'ERR',
            'descricao_erro':
                'Erro ao criar registro de quantidade solicitada',
        })
        return JsonResponse(data, safe=False)

    data = {
        'result': 'OK',
        'solicitacao_id': solicitacao_id,
        'lote': lote,
        'qtd': iqtd,
        'solicita_qtd_id': solicita.id,
    }
    return JsonResponse(data, safe=False)
